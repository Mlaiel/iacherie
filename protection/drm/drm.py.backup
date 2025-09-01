"""🔐 Digital Rights Management (DRM) System
========================================

Ultra-advanced DRM protection and license management system:
- Multi-format content encryption and protection
- Dynamic licensing and access control
- Real-time usage monitoring and enforcement
- Secure key management and distribution
- Cross-platform DRM integration
- Advanced piracy prevention mechanisms

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Cryptography Expert + DRM Specialist + Security Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import json
import base64
import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import time
import jwt
from concurrent.futures import ThreadPoolExecutor
import aiohttp

logger = logging.getLogger(__name__)

class DRMProtectionLevel(Enum):
    """DRM protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MILITARY_GRADE = "military_grade"

class ContentFormat(Enum):
    """Supported content formats"""
    AUDIO_MP3 = "audio_mp3"
    AUDIO_FLAC = "audio_flac"
    AUDIO_WAV = "audio_wav"
    VIDEO_MP4 = "video_mp4"
    VIDEO_AVI = "video_avi"
    VIDEO_MKV = "video_mkv"
    IMAGE_JPEG = "image_jpeg"
    IMAGE_PNG = "image_png"
    DOCUMENT_PDF = "document_pdf"
    EBOOK_EPUB = "ebook_epub"

class LicenseType(Enum):
    """License types"""
    SINGLE_USE = "single_use"
    TIME_LIMITED = "time_limited"
    DEVICE_BOUND = "device_bound"
    USER_BOUND = "user_bound"
    SUBSCRIPTION = "subscription"
    RENTAL = "rental"
    ENTERPRISE = "enterprise"

class EncryptionAlgorithm(Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"
    HYBRID_AES_RSA = "hybrid_aes_rsa"

@dataclass
class DRMProtectedContent:
    """DRM protected content structure"""
    content_id: str
    original_format: ContentFormat
    protection_level: DRMProtectionLevel
    encryption_algorithm: EncryptionAlgorithm
    encrypted_content: bytes
    content_key_id: str
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int
    max_access_count: Optional[int]

@dataclass
class DRMLicense:
    """DRM license structure"""
    license_id: str
    content_id: str
    user_id: str
    license_type: LicenseType
    device_fingerprint: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    usage_count: int
    max_usage_count: Optional[int]
    permissions: Dict[str, bool]
    license_data: bytes
    created_at: datetime
    last_used: Optional[datetime]

@dataclass
class ContentKey:
    """Content encryption key structure"""
    key_id: str
    content_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    iv: Optional[bytes]
    salt: Optional[bytes]
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int
    rotation_required: bool

class AdvancedDRMSystem:
    """
    Ultra-advanced Digital Rights Management system
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.protected_content = {}
        self.licenses = {}
        self.content_keys = {}
        self.user_sessions = {}
        self.device_registry = {}
        
        # DRM configuration
        self.drm_config = {
            'key_rotation_interval': 86400,  # 24 hours
            'max_concurrent_sessions': 3,
            'license_validation_interval': 300,  # 5 minutes
            'device_fingerprint_required': True,
            'geographic_restrictions': True,
            'offline_license_duration': 604800,  # 7 days
            'content_key_cache_duration': 3600,  # 1 hour
            'encryption_parameters': {
                'aes_key_size': 256,
                'rsa_key_size': 4096,
                'pbkdf2_iterations': 100000,
                'gcm_tag_size': 16
            }
        }
        
        # Protection level configurations
        self.protection_configs = {
            DRMProtectionLevel.BASIC: {
                'encryption': EncryptionAlgorithm.AES_256_CBC,
                'key_rotation_hours': 168,  # 1 week
                'max_devices': 5,
                'offline_allowed': True,
                'watermarking': False
            },
            DRMProtectionLevel.STANDARD: {
                'encryption': EncryptionAlgorithm.AES_256_GCM,
                'key_rotation_hours': 72,  # 3 days
                'max_devices': 3,
                'offline_allowed': True,
                'watermarking': True
            },
            DRMProtectionLevel.PREMIUM: {
                'encryption': EncryptionAlgorithm.HYBRID_AES_RSA,
                'key_rotation_hours': 24,  # 1 day
                'max_devices': 2,
                'offline_allowed': False,
                'watermarking': True
            },
            DRMProtectionLevel.ENTERPRISE: {
                'encryption': EncryptionAlgorithm.HYBRID_AES_RSA,
                'key_rotation_hours': 12,  # 12 hours
                'max_devices': 1,
                'offline_allowed': False,
                'watermarking': True
            },
            DRMProtectionLevel.MILITARY_GRADE: {
                'encryption': EncryptionAlgorithm.CHACHA20_POLY1305,
                'key_rotation_hours': 1,  # 1 hour
                'max_devices': 1,
                'offline_allowed': False,
                'watermarking': True
            }
        }
        
        # Initialize cryptographic components
        self._initialize_crypto_components()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced DRM System initialized")
    
    def _initialize_crypto_components(self):
        """Initialize cryptographic components"""
        try:
            # Generate master keys
            self.master_key = self._generate_master_key()
            self.signing_key = self._generate_signing_key()
            
            # Initialize key derivation
            self.kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'drm_salt_2025',
                iterations=self.drm_config['encryption_parameters']['pbkdf2_iterations']
            )
            
            logger.info("Cryptographic components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize crypto components: {str(e)}")
            raise
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        try:
            # Key rotation task
            asyncio.create_task(self._key_rotation_task())
            
            # License validation task
            asyncio.create_task(self._license_validation_task())
            
            # Usage monitoring task
            asyncio.create_task(self._usage_monitoring_task())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {str(e)}")
    
    async def protect_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply DRM protection to content"""
        try:
            content_id = content_data['content_id']
            content_path = content_data['content_path']
            protection_level = DRMProtectionLevel(content_data['protection_level'])
            content_format = ContentFormat(content_data['content_format'])
            
            # Get protection configuration
            protection_config = self.protection_configs[protection_level]
            
            # Read original content
            with open(content_path, 'rb') as f:
                original_content = f.read()
            
            # Generate content encryption key
            content_key = await self._generate_content_key(
                content_id, protection_config['encryption']
            )
            
            # Encrypt content
            encrypted_content = await self._encrypt_content(
                original_content, content_key, protection_config['encryption']
            )
            
            # Apply watermarking if enabled
            if protection_config['watermarking']:
                encrypted_content = await self._apply_watermarking(
                    encrypted_content, content_id, content_format
                )
            
            # Create protected content record
            protected_content = DRMProtectedContent(
                content_id=content_id,
                original_format=content_format,
                protection_level=protection_level,
                encryption_algorithm=protection_config['encryption'],
                encrypted_content=encrypted_content,
                content_key_id=content_key.key_id,
                metadata={
                    'original_size': len(original_content),
                    'encrypted_size': len(encrypted_content),
                    'protection_config': asdict(protection_config),
                    'checksum': hashlib.sha256(original_content).hexdigest()
                },
                created_at=datetime.utcnow(),
                expires_at=content_data.get('expires_at'),
                access_count=0,
                max_access_count=content_data.get('max_access_count')
            )
            
            # Store protected content
            self.protected_content[content_id] = protected_content
            self.content_keys[content_key.key_id] = content_key
            
            # Generate content manifest
            content_manifest = await self._generate_content_manifest(protected_content)
            
            protection_result = {
                'content_id': content_id,
                'protection_level': protection_level.value,
                'encryption_algorithm': protection_config['encryption'].value,
                'content_key_id': content_key.key_id,
                'protected_size': len(encrypted_content),
                'watermarked': protection_config['watermarking'],
                'manifest': content_manifest,
                'protected_at': protected_content.created_at.isoformat()
            }
            
            logger.info(f"Content protected: {content_id} with {protection_level.value} protection")
            
            return protection_result
            
        except Exception as e:
            logger.error(f"Content protection failed: {str(e)}")
            raise
    
    async def generate_license(self, license_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DRM license for content access"""
        try:
            content_id = license_request['content_id']
            user_id = license_request['user_id']
            license_type = LicenseType(license_request['license_type'])
            device_info = license_request.get('device_info', {})
            
            # Verify content exists
            if content_id not in self.protected_content:
                raise ValueError(f"Protected content not found: {content_id}")
            
            protected_content = self.protected_content[content_id]
            
            # Generate device fingerprint
            device_fingerprint = self._generate_device_fingerprint(device_info)
            
            # Validate license request
            validation_result = await self._validate_license_request(
                license_request, protected_content, device_fingerprint
            )
            
            if not validation_result['valid']:
                raise ValueError(f"License request validation failed: {validation_result['errors']}")
            
            # Determine license parameters
            license_params = await self._calculate_license_parameters(
                license_type, protected_content, license_request
            )
            
            # Generate license data
            license_data = await self._generate_license_data(
                content_id, user_id, device_fingerprint, license_params
            )
            
            # Create license record
            license_record = DRMLicense(
                license_id=str(uuid.uuid4()),
                content_id=content_id,
                user_id=user_id,
                license_type=license_type,
                device_fingerprint=device_fingerprint,
                valid_from=datetime.utcnow(),
                valid_until=license_params['valid_until'],
                usage_count=0,
                max_usage_count=license_params['max_usage_count'],
                permissions=license_params['permissions'],
                license_data=license_data,
                created_at=datetime.utcnow(),
                last_used=None
            )
            
            # Store license
            self.licenses[license_record.license_id] = license_record
            
            # Update user session
            await self._update_user_session(user_id, device_fingerprint, license_record)
            
            license_response = {
                'license_id': license_record.license_id,
                'content_id': content_id,
                'license_type': license_type.value,
                'valid_from': license_record.valid_from.isoformat(),
                'valid_until': license_record.valid_until.isoformat() if license_record.valid_until else None,
                'max_usage_count': license_record.max_usage_count,
                'permissions': license_record.permissions,
                'device_fingerprint': device_fingerprint,
                'license_token': self._generate_license_token(license_record)
            }
            
            logger.info(f"License generated: {license_record.license_id} for content {content_id}")
            
            return license_response
            
        except Exception as e:
            logger.error(f"License generation failed: {str(e)}")
            raise
    
    async def decrypt_content(self, access_request: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt and provide access to protected content"""
        try:
            license_token = access_request['license_token']
            content_id = access_request['content_id']
            device_info = access_request.get('device_info', {})
            
            # Validate license token
            license_data = self._validate_license_token(license_token)
            if not license_data:
                raise ValueError("Invalid or expired license token")
            
            license_id = license_data['license_id']
            
            # Find license record
            if license_id not in self.licenses:
                raise ValueError(f"License not found: {license_id}")
            
            license_record = self.licenses[license_id]
            
            # Verify content access
            access_validation = await self._validate_content_access(
                license_record, content_id, device_info
            )
            
            if not access_validation['allowed']:
                raise ValueError(f"Access denied: {access_validation['reason']}")
            
            # Get protected content
            protected_content = self.protected_content[content_id]
            
            # Get content key
            content_key = self.content_keys[protected_content.content_key_id]
            
            # Decrypt content
            decrypted_content = await self._decrypt_content(
                protected_content.encrypted_content,
                content_key,
                protected_content.encryption_algorithm
            )
            
            # Update usage tracking
            await self._update_usage_tracking(license_record, protected_content)
            
            # Generate temporary access URL or stream key
            access_method = access_request.get('access_method', 'direct')
            if access_method == 'stream':
                access_data = await self._generate_streaming_access(
                    decrypted_content, license_record
                )
            else:
                access_data = {
                    'content_data': base64.b64encode(decrypted_content).decode(),
                    'content_type': protected_content.original_format.value,
                    'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
            
            # Log access event
            await self._log_access_event(license_record, protected_content, device_info)
            
            access_response = {
                'content_id': content_id,
                'license_id': license_id,
                'access_granted': True,
                'access_method': access_method,
                'usage_count': license_record.usage_count,
                'remaining_uses': (license_record.max_usage_count - license_record.usage_count) 
                                if license_record.max_usage_count else None,
                'access_data': access_data,
                'accessed_at': datetime.utcnow().isoformat()
            }
            
            return access_response
            
        except Exception as e:
            logger.error(f"Content decryption failed: {str(e)}")
            raise
    
    async def revoke_license(self, revocation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke DRM license"""
        try:
            license_id = revocation_request['license_id']
            revocation_reason = revocation_request.get('reason', 'user_request')
            
            # Find license
            if license_id not in self.licenses:
                raise ValueError(f"License not found: {license_id}")
            
            license_record = self.licenses[license_id]
            
            # Update license to revoked status
            license_record.valid_until = datetime.utcnow()
            license_record.metadata = license_record.metadata or {}
            license_record.metadata.update({
                'revoked': True,
                'revocation_reason': revocation_reason,
                'revoked_at': datetime.utcnow().isoformat()
            })
            
            # Remove from active sessions
            await self._remove_from_active_sessions(license_record)
            
            # Invalidate cached keys
            await self._invalidate_cached_keys(license_record.content_id)
            
            revocation_result = {
                'license_id': license_id,
                'revoked': True,
                'revocation_reason': revocation_reason,
                'revoked_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"License revoked: {license_id} - {revocation_reason}")
            
            return revocation_result
            
        except Exception as e:
            logger.error(f"License revocation failed: {str(e)}")
            raise
    
    async def generate_usage_report(self, report_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive DRM usage report"""
        try:
            content_id = report_request.get('content_id')
            user_id = report_request.get('user_id')
            time_period = report_request.get('time_period', 'month')
            
            # Filter data based on request
            filtered_licenses = self._filter_licenses_for_report(
                content_id, user_id, time_period
            )
            
            if not filtered_licenses:
                return {'message': 'No usage data found for specified criteria'}
            
            # Calculate usage statistics
            usage_stats = await self._calculate_usage_statistics(filtered_licenses)
            
            # Analyze protection effectiveness
            protection_analysis = await self._analyze_protection_effectiveness(filtered_licenses)
            
            # Generate revenue impact analysis
            revenue_analysis = await self._analyze_revenue_impact(filtered_licenses)
            
            # Compliance and security metrics
            security_metrics = await self._calculate_security_metrics(filtered_licenses)
            
            # Device and platform analytics
            device_analytics = await self._analyze_device_usage(filtered_licenses)
            
            usage_report = {
                'report_period': time_period,
                'generated_at': datetime.utcnow().isoformat(),
                'scope': {
                    'content_id': content_id,
                    'user_id': user_id,
                    'licenses_analyzed': len(filtered_licenses)
                },
                'usage_statistics': usage_stats,
                'protection_analysis': protection_analysis,
                'revenue_analysis': revenue_analysis,
                'security_metrics': security_metrics,
                'device_analytics': device_analytics,
                'recommendations': await self._generate_drm_recommendations(filtered_licenses)
            }
            
            return usage_report
            
        except Exception as e:
            logger.error(f"Usage report generation failed: {str(e)}")
            raise
    
    # Encryption and decryption methods
    async def _encrypt_content(self, content: bytes, content_key: 'ContentKey', 
                             algorithm: EncryptionAlgorithm) -> bytes:
        """Encrypt content using specified algorithm"""
        try:
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._encrypt_aes_gcm(content, content_key)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._encrypt_aes_cbc(content, content_key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return await self._encrypt_chacha20(content, content_key)
            elif algorithm == EncryptionAlgorithm.HYBRID_AES_RSA:
                return await self._encrypt_hybrid(content, content_key)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
            
        except Exception as e:
            logger.error(f"Content encryption failed: {str(e)}")
            raise
    
    async def _encrypt_aes_gcm(self, content: bytes, content_key: 'ContentKey') -> bytes:
        """Encrypt content using AES-256-GCM"""
        try:
            # Generate nonce
            nonce = os.urandom(12)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(content_key.key_data),
                modes.GCM(nonce)
            )
            encryptor = cipher.encryptor()
            
            # Encrypt content
            ciphertext = encryptor.update(content) + encryptor.finalize()
            
            # Combine nonce, tag, and ciphertext
            encrypted_data = nonce + encryptor.tag + ciphertext
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"AES-GCM encryption failed: {str(e)}")
            raise
    
    async def _encrypt_aes_cbc(self, content: bytes, content_key: 'ContentKey') -> bytes:
        """Encrypt content using AES-256-CBC"""
        try:
            # Pad content to block size
            block_size = 16
            padding_length = block_size - (len(content) % block_size)
            padded_content = content + bytes([padding_length] * padding_length)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(content_key.key_data),
                modes.CBC(content_key.iv)
            )
            encryptor = cipher.encryptor()
            
            # Encrypt content
            ciphertext = encryptor.update(padded_content) + encryptor.finalize()
            
            # Combine IV and ciphertext
            encrypted_data = content_key.iv + ciphertext
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"AES-CBC encryption failed: {str(e)}")
            raise
    
    async def _encrypt_chacha20(self, content: bytes, content_key: 'ContentKey') -> bytes:
        """Encrypt content using ChaCha20-Poly1305"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            
            # Create ChaCha20Poly1305 instance
            chacha = ChaCha20Poly1305(content_key.key_data)
            
            # Generate nonce
            nonce = os.urandom(12)
            
            # Encrypt content
            ciphertext = chacha.encrypt(nonce, content, None)
            
            # Combine nonce and ciphertext
            encrypted_data = nonce + ciphertext
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"ChaCha20-Poly1305 encryption failed: {str(e)}")
            raise
    
    async def _decrypt_content(self, encrypted_content: bytes, content_key: 'ContentKey',
                             algorithm: EncryptionAlgorithm) -> bytes:
        """Decrypt content using specified algorithm"""
        try:
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._decrypt_aes_gcm(encrypted_content, content_key)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._decrypt_aes_cbc(encrypted_content, content_key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return await self._decrypt_chacha20(encrypted_content, content_key)
            elif algorithm == EncryptionAlgorithm.HYBRID_AES_RSA:
                return await self._decrypt_hybrid(encrypted_content, content_key)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {algorithm}")
            
        except Exception as e:
            logger.error(f"Content decryption failed: {str(e)}")
            raise
    
    # Key management methods
    async def _generate_content_key(self, content_id: str, 
                                  algorithm: EncryptionAlgorithm) -> ContentKey:
        """Generate content encryption key"""
        try:
            key_id = str(uuid.uuid4())
            
            if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key_data = os.urandom(32)  # 256 bits
                iv = os.urandom(16) if algorithm == EncryptionAlgorithm.AES_256_CBC else None
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_data = os.urandom(32)  # 256 bits
                iv = None
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                # Generate RSA key pair
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096
                )
                key_data = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                iv = None
            else:
                key_data = os.urandom(32)
                iv = None
            
            content_key = ContentKey(
                key_id=key_id,
                content_id=content_id,
                algorithm=algorithm,
                key_data=key_data,
                iv=iv,
                salt=os.urandom(32),
                created_at=datetime.utcnow(),
                expires_at=None,
                usage_count=0,
                rotation_required=False
            )
            
            return content_key
            
        except Exception as e:
            logger.error(f"Content key generation failed: {str(e)}")
            raise
    
    def _generate_master_key(self) -> bytes:
        """Generate master encryption key"""
        return os.urandom(32)  # 256-bit key
    
    def _generate_signing_key(self) -> bytes:
        """Generate signing key for license tokens"""
        return os.urandom(64)  # 512-bit key
    
    # Device and session management
    def _generate_device_fingerprint(self, device_info: Dict[str, Any]) -> str:
        """Generate unique device fingerprint"""
        try:
            # Combine device characteristics
            fingerprint_data = [
                device_info.get('hardware_id', ''),
                device_info.get('os_version', ''),
                device_info.get('browser_version', ''),
                device_info.get('screen_resolution', ''),
                device_info.get('timezone', ''),
                device_info.get('language', ''),
                str(device_info.get('cpu_cores', 0)),
                str(device_info.get('memory_gb', 0))
            ]
            
            # Create fingerprint hash
            fingerprint_string = '|'.join(fingerprint_data)
            fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()
            
            return fingerprint_hash[:32]  # Use first 32 characters
            
        except Exception as e:
            logger.error(f"Device fingerprint generation failed: {str(e)}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
    
    # License validation and management
    async def _validate_license_request(self, request: Dict[str, Any], 
                                      protected_content: DRMProtectedContent,
                                      device_fingerprint: str) -> Dict[str, Any]:
        """Validate license request"""
        errors = []
        
        # Check content availability
        if protected_content.expires_at and protected_content.expires_at < datetime.utcnow():
            errors.append("Content has expired")
        
        # Check access count limits
        if (protected_content.max_access_count and 
            protected_content.access_count >= protected_content.max_access_count):
            errors.append("Content access limit exceeded")
        
        # Check device limits for user
        user_id = request['user_id']
        user_devices = self._get_user_devices(user_id)
        protection_config = self.protection_configs[protected_content.protection_level]
        
        if len(user_devices) >= protection_config['max_devices']:
            if device_fingerprint not in user_devices:
                errors.append("Device limit exceeded")
        
        # Geographic restrictions (if enabled)
        if self.drm_config['geographic_restrictions']:
            user_location = request.get('location')
            if user_location and not self._validate_geographic_access(user_location):
                errors.append("Geographic restriction violation")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_license_token(self, license_record: DRMLicense) -> str:
        """Generate JWT token for license"""
        try:
            payload = {
                'license_id': license_record.license_id,
                'content_id': license_record.content_id,
                'user_id': license_record.user_id,
                'device_fingerprint': license_record.device_fingerprint,
                'valid_from': license_record.valid_from.timestamp(),
                'valid_until': license_record.valid_until.timestamp() if license_record.valid_until else None,
                'permissions': license_record.permissions,
                'iat': time.time(),
                'exp': license_record.valid_until.timestamp() if license_record.valid_until else time.time() + 86400
            }
            
            token = jwt.encode(payload, self.signing_key, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"License token generation failed: {str(e)}")
            raise
    
    def _validate_license_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decode license token"""
        try:
            payload = jwt.decode(token, self.signing_key, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("License token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid license token: {str(e)}")
            return None
    
    # Background tasks
    async def _key_rotation_task(self):
        """Background task for key rotation"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                current_time = datetime.utcnow()
                
                # Check keys that need rotation
                for key_id, content_key in list(self.content_keys.items()):
                    if content_key.rotation_required:
                        await self._rotate_content_key(content_key)
                
                logger.debug("Key rotation check completed")
                
            except Exception as e:
                logger.error(f"Key rotation task failed: {str(e)}")
    
    async def _license_validation_task(self):
        """Background task for license validation"""
        while True:
            try:
                await asyncio.sleep(self.drm_config['license_validation_interval'])
                
                current_time = datetime.utcnow()
                expired_licenses = []
                
                # Check for expired licenses
                for license_id, license_record in self.licenses.items():
                    if (license_record.valid_until and 
                        license_record.valid_until < current_time):
                        expired_licenses.append(license_id)
                
                # Remove expired licenses
                for license_id in expired_licenses:
                    del self.licenses[license_id]
                    logger.debug(f"Expired license removed: {license_id}")
                
            except Exception as e:
                logger.error(f"License validation task failed: {str(e)}")
    
    async def _usage_monitoring_task(self):
        """Background task for usage monitoring"""
        while True:
            try:
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
                # Monitor for suspicious usage patterns
                await self._detect_suspicious_usage()
                
                # Update usage statistics
                await self._update_usage_statistics()
                
                logger.debug("Usage monitoring completed")
                
            except Exception as e:
                logger.error(f"Usage monitoring task failed: {str(e)}")
    
    # Helper methods
    def _get_user_devices(self, user_id: str) -> List[str]:
        """Get list of devices for user"""
        user_devices = []
        for license in self.licenses.values():
            if (license.user_id == user_id and 
                license.device_fingerprint and 
                license.device_fingerprint not in user_devices):
                user_devices.append(license.device_fingerprint)
        return user_devices
    
    def _validate_geographic_access(self, location: Dict[str, Any]) -> bool:
        """Validate geographic access restrictions"""
        # Implement geographic validation logic
        # This is a placeholder implementation
        allowed_countries = self.config.get('allowed_countries', [])
        if allowed_countries:
            return location.get('country') in allowed_countries
        return True
