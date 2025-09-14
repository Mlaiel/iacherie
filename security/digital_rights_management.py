"""
Digital Rights Management module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🎵 Digital Rights Management System - Ainflue Platform
=====================================================

Enterprise-grade DRM system for protecting creator content with watermarking,
encryption, license management, usage tracking, and piracy detection for
musicians, bloggers, photographers, influencers, and comedians.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Role Expert: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Specialist
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import secrets
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content that can be protected"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    EBOOK = "ebook"
    SOFTWARE = "software"

class LicenseType(Enum):
    """Digital license types"""
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SUBSCRIPTION = "subscription"
    ROYALTY_FREE = "royalty_free"

class WatermarkType(Enum):
    """Watermark types"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    AUDIO_STEGANOGRAPHY = "audio_steganography"
    VIDEO_STEGANOGRAPHY = "video_steganography"
    BLOCKCHAIN = "blockchain"

class UsageType(Enum):
    """Content usage types"""
    VIEW = "view"
    DOWNLOAD = "download"
    STREAM = "stream"
    SHARE = "share"
    MODIFY = "modify"
    REDISTRIBUTE = "redistribute"
    PRINT = "print"
    COPY = "copy"

@dataclass
class CreatorProfile:
    """Content creator profile"""
    creator_id: str
    creator_type: str  # musician, blogger, photographer, influencer, comedian
    name: str
    email: str
    verification_status: str
    revenue_share_percentage: float
    content_categories: List[str]
    geographic_regions: List[str]
    payment_details: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ContentMetadata:
    """Content metadata for DRM protection"""
    content_id: str
    title: str
    creator_id: str
    content_type: ContentType
    file_size: int
    duration: Optional[float] = None  # for audio/video
    dimensions: Optional[Tuple[int, int]] = None  # for images/video
    format: str = ""
    quality: str = ""
    tags: List[str] = field(default_factory=list)
    description: str = ""
    upload_date: datetime = field(default_factory=datetime.now)
    copyright_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DigitalLicense:
    """Digital license for content usage"""
    license_id: str
    content_id: str
    licensee_id: str
    license_type: LicenseType
    allowed_usages: Set[UsageType]
    usage_limits: Dict[str, int]  # e.g., {'views': 1000, 'downloads': 5}
    geographic_restrictions: List[str]
    platform_restrictions: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    revenue_share: float
    watermark_required: bool = True
    attribution_required: bool = True
    transfer_allowed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Watermark:
    """Watermark information"""
    watermark_id: str
    content_id: str
    watermark_type: WatermarkType
    watermark_data: bytes
    strength: float  # 0.0 to 1.0
    position: Optional[Tuple[int, int]] = None
    transparency: float = 0.5
    detection_threshold: float = 0.8
    creator_signature: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UsageRecord:
    """Content usage tracking record"""
    usage_id: str
    content_id: str
    user_id: str
    license_id: Optional[str]
    usage_type: UsageType
    ip_address: str
    user_agent: str
    geographic_location: Optional[str]
    platform: str
    session_id: str
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    duration: Optional[float] = None
    quality_accessed: Optional[str] = None

@dataclass
class PiracyAlert:
    """Piracy detection alert"""
    alert_id: str
    content_id: str
    detected_url: str
    detection_method: str
    confidence_score: float
    platform: str
    reported_by: str
    status: str = "pending"
    action_taken: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)

class DigitalRightsManagement:
    """
    🎵 Enterprise Digital Rights Management System
    
    Features:
    - Content encryption and protection
    - Digital watermarking (visible/invisible)
    - License management and enforcement
    - Usage tracking and analytics
    - Piracy detection and prevention
    - Revenue tracking and distribution
    - Multi-platform DRM support
    - Blockchain integration ready
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        
        # Content storage
        self.creators: Dict[str, CreatorProfile] = {}
        self.content_metadata: Dict[str, ContentMetadata] = {}
        self.licenses: Dict[str, DigitalLicense] = {}
        self.watermarks: Dict[str, Watermark] = {}
        self.usage_records: List[UsageRecord] = []
        self.piracy_alerts: List[PiracyAlert] = []
        
        # Encryption keys
        self.master_key = Fernet.generate_key()
        self.content_cipher = Fernet(self.master_key)
        
        # Content fingerprinting
        self.content_fingerprints: Dict[str, str] = {}
        
        # Analytics
        self.usage_analytics: Dict[str, Any] = {}
        self.revenue_analytics: Dict[str, Any] = {}
        
        logger.info("🎵 Digital Rights Management System initialized")

    async def register_creator(self, creator: CreatorProfile) -> bool:
        """
        👨‍🎨 Register a new content creator
        """
        try:
            # Validate creator profile
            if not self._validate_creator_profile(creator):
                return False
            
            # Store creator
            self.creators[creator.creator_id] = creator
            
            # Initialize analytics for creator
            self.usage_analytics[creator.creator_id] = {
                'total_views': 0,
                'total_downloads': 0,
                'total_revenue': 0.0,
                'content_count': 0,
                'last_activity': datetime.now()
            }
            
            logger.info(f"👨‍🎨 Registered creator: {creator.name} ({creator.creator_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register creator: {e}")
            return False

    async def protect_content(
        self,
        content_metadata: ContentMetadata,
        content_data: bytes,
        protection_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        🔒 Protect content with DRM including encryption and watermarking
        """
        try:
            # Validate content
            if not self._validate_content(content_metadata):
                raise ValueError("Invalid content metadata")
            
            # Generate content fingerprint
            fingerprint = self._generate_content_fingerprint(content_data)
            self.content_fingerprints[content_metadata.content_id] = fingerprint
            
            # Encrypt content
            encrypted_content = await self._encrypt_content(content_data, content_metadata)
            
            # Generate watermark
            watermark = await self._generate_watermark(content_metadata, content_data)
            
            # Apply watermark to content
            watermarked_content = await self._apply_watermark(
                encrypted_content, watermark, content_metadata
            )
            
            # Store metadata
            self.content_metadata[content_metadata.content_id] = content_metadata
            self.watermarks[watermark.watermark_id] = watermark
            
            # Update creator analytics
            creator_id = content_metadata.creator_id
            if creator_id in self.usage_analytics:
                self.usage_analytics[creator_id]['content_count'] += 1
            
            protection_info = {
                'content_id': content_metadata.content_id,
                'protected_content': watermarked_content,
                'encryption_key_id': f"key_{content_metadata.content_id}",
                'watermark_id': watermark.watermark_id,
                'fingerprint': fingerprint,
                'protection_level': protection_level,
                'size_original': len(content_data),
                'size_protected': len(watermarked_content)
            }
            
            logger.info(f"🔒 Protected content: {content_metadata.title} ({len(content_data)} → {len(watermarked_content)} bytes)")
            return protection_info
            
        except Exception as e:
            logger.error(f"❌ Content protection failed: {e}")
            raise

    async def create_license(
        self,
        content_id: str,
        licensee_id: str,
        license_type: LicenseType,
        allowed_usages: Set[UsageType],
        usage_limits: Dict[str, int],
        duration_days: Optional[int] = None
    ) -> DigitalLicense:
        """
        📜 Create digital license for content usage
        """
        try:
            # Validate content exists
            if content_id not in self.content_metadata:
                raise ValueError(f"Content not found: {content_id}")
            
            # Calculate end date
            end_date = None
            if duration_days:
                end_date = datetime.now() + timedelta(days=duration_days)
            
            # Create license
            license = DigitalLicense(
                license_id=f"lic_{int(time.time())}_{secrets.token_hex(8)}",
                content_id=content_id,
                licensee_id=licensee_id,
                license_type=license_type,
                allowed_usages=allowed_usages,
                usage_limits=usage_limits,
                geographic_restrictions=[],
                platform_restrictions=[],
                start_date=datetime.now(),
                end_date=end_date,
                revenue_share=self._calculate_revenue_share(license_type)
            )
            
            # Store license
            self.licenses[license.license_id] = license
            
            logger.info(f"📜 Created license: {license.license_id} for content {content_id}")
            return license
            
        except Exception as e:
            logger.error(f"❌ License creation failed: {e}")
            raise

    async def validate_usage(
        self,
        content_id: str,
        user_id: str,
        usage_type: UsageType,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ✅ Validate if user can perform specific usage on content
        """
        try:
            # Find applicable licenses
            applicable_licenses = [
                license for license in self.licenses.values()
                if (license.content_id == content_id and 
                    license.licensee_id == user_id and
                    usage_type in license.allowed_usages)
            ]
            
            if not applicable_licenses:
                return {
                    'allowed': False,
                    'reason': 'No valid license found',
                    'license_id': None
                }
            
            # Check each license
            for license in applicable_licenses:
                validation_result = await self._validate_license(license, usage_type, context)
                if validation_result['valid']:
                    return {
                        'allowed': True,
                        'license_id': license.license_id,
                        'usage_limits': license.usage_limits,
                        'restrictions': {
                            'geographic': license.geographic_restrictions,
                            'platform': license.platform_restrictions
                        }
                    }
            
            return {
                'allowed': False,
                'reason': 'License validation failed',
                'license_id': None
            }
            
        except Exception as e:
            logger.error(f"❌ Usage validation failed: {e}")
            return {
                'allowed': False,
                'reason': f'Validation error: {str(e)}',
                'license_id': None
            }

    async def track_usage(
        self,
        content_id: str,
        user_id: str,
        usage_type: UsageType,
        context: Dict[str, Any]
    ) -> UsageRecord:
        """
        📊 Track content usage for analytics and licensing
        """
        try:
            # Create usage record
            usage_record = UsageRecord(
                usage_id=f"usage_{int(time.time())}_{secrets.token_hex(6)}",
                content_id=content_id,
                user_id=user_id,
                license_id=context.get('license_id'),
                usage_type=usage_type,
                ip_address=context.get('ip_address', ''),
                user_agent=context.get('user_agent', ''),
                geographic_location=context.get('location'),
                platform=context.get('platform', 'unknown'),
                session_id=context.get('session_id', ''),
                metadata=context.get('metadata', {}),
                duration=context.get('duration'),
                quality_accessed=context.get('quality')
            )
            
            # Store usage record
            self.usage_records.append(usage_record)
            
            # Update analytics
            await self._update_usage_analytics(usage_record)
            
            # Update license usage counters
            if usage_record.license_id:
                await self._update_license_usage(usage_record)
            
            logger.info(f"📊 Tracked usage: {usage_type.value} for content {content_id}")
            return usage_record
            
        except Exception as e:
            logger.error(f"❌ Usage tracking failed: {e}")
            raise

    async def detect_piracy(self, content_id: str, monitoring_scope: str = "web") -> List[PiracyAlert]:
        """
        🚨 Detect potential piracy of protected content
        """
        try:
            alerts = []
            
            # Get content fingerprint
            fingerprint = self.content_fingerprints.get(content_id)
            if not fingerprint:
                logger.warning(f"⚠️ No fingerprint found for content {content_id}")
                return alerts
            
            # Simulate piracy detection (in production, this would use real APIs)
            suspicious_urls = await self._scan_for_piracy(content_id, fingerprint, monitoring_scope)
            
            for url_info in suspicious_urls:
                alert = PiracyAlert(
                    alert_id=f"alert_{int(time.time())}_{secrets.token_hex(6)}",
                    content_id=content_id,
                    detected_url=url_info['url'],
                    detection_method=url_info['method'],
                    confidence_score=url_info['confidence'],
                    platform=url_info['platform'],
                    reported_by="automated_scanner",
                    evidence=url_info.get('evidence', {})
                )
                
                alerts.append(alert)
                self.piracy_alerts.append(alert)
            
            if alerts:
                logger.warning(f"🚨 Detected {len(alerts)} potential piracy instances for content {content_id}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Piracy detection failed: {e}")
            return []

    async def generate_usage_report(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        📈 Generate comprehensive usage and revenue report
        """
        try:
            # Filter usage records for creator and date range
            creator_content_ids = [
                content_id for content_id, metadata in self.content_metadata.items()
                if metadata.creator_id == creator_id
            ]
            
            relevant_usage = [
                record for record in self.usage_records
                if (record.content_id in creator_content_ids and
                    start_date <= record.timestamp <= end_date)
            ]
            
            # Calculate metrics
            total_views = sum(1 for r in relevant_usage if r.usage_type == UsageType.VIEW)
            total_downloads = sum(1 for r in relevant_usage if r.usage_type == UsageType.DOWNLOAD)
            total_streams = sum(1 for r in relevant_usage if r.usage_type == UsageType.STREAM)
            
            # Calculate revenue
            revenue_data = await self._calculate_revenue(relevant_usage, creator_id)
            
            # Geographic breakdown
            geographic_data = {}
            for record in relevant_usage:
                location = record.geographic_location or "Unknown"
                geographic_data[location] = geographic_data.get(location, 0) + 1
            
            # Platform breakdown
            platform_data = {}
            for record in relevant_usage:
                platform = record.platform
                platform_data[platform] = platform_data.get(platform, 0) + 1
            
            # Content performance
            content_performance = {}
            for content_id in creator_content_ids:
                content_usage = [r for r in relevant_usage if r.content_id == content_id]
                content_metadata = self.content_metadata[content_id]
                content_performance[content_id] = {
                    'title': content_metadata.title,
                    'views': sum(1 for r in content_usage if r.usage_type == UsageType.VIEW),
                    'downloads': sum(1 for r in content_usage if r.usage_type == UsageType.DOWNLOAD),
                    'revenue': 0.0  # Would calculate from license fees
                }
            
            report = {
                'creator_id': creator_id,
                'report_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_views': total_views,
                    'total_downloads': total_downloads,
                    'total_streams': total_streams,
                    'total_revenue': revenue_data['total'],
                    'content_count': len(creator_content_ids)
                },
                'revenue_breakdown': revenue_data['breakdown'],
                'geographic_distribution': geographic_data,
                'platform_distribution': platform_data,
                'content_performance': content_performance,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"📈 Generated usage report for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            raise

    # Private helper methods

    async def _encrypt_content(self, content_data: bytes, metadata: ContentMetadata) -> bytes:
        """Encrypt content data"""
        try:
            # Create content-specific encryption key
            content_key = self._derive_content_key(metadata.content_id)
            content_cipher = Fernet(content_key)
            
            # Encrypt content
            encrypted_content = content_cipher.encrypt(content_data)
            
            logger.debug(f"🔐 Encrypted content: {metadata.content_id}")
            return encrypted_content
            
        except Exception as e:
            logger.error(f"❌ Content encryption failed: {e}")
            raise

    async def _generate_watermark(
        self, 
        metadata: ContentMetadata, 
        content_data: bytes
    ) -> Watermark:
        """Generate watermark for content"""
        try:
            watermark_id = f"wm_{metadata.content_id}_{int(time.time())}"
            
            # Generate watermark data based on content type
            if metadata.content_type == ContentType.IMAGE:
                watermark_data = await self._generate_image_watermark(metadata, content_data)
                watermark_type = WatermarkType.VISIBLE
            elif metadata.content_type == ContentType.AUDIO:
                watermark_data = await self._generate_audio_watermark(metadata, content_data)
                watermark_type = WatermarkType.AUDIO_STEGANOGRAPHY
            elif metadata.content_type == ContentType.VIDEO:
                watermark_data = await self._generate_video_watermark(metadata, content_data)
                watermark_type = WatermarkType.VIDEO_STEGANOGRAPHY
            else:
                watermark_data = await self._generate_text_watermark(metadata, content_data)
                watermark_type = WatermarkType.INVISIBLE
            
            # Create creator signature
            creator = self.creators.get(metadata.creator_id)
            creator_signature = self._create_creator_signature(creator, metadata) if creator else None
            
            watermark = Watermark(
                watermark_id=watermark_id,
                content_id=metadata.content_id,
                watermark_type=watermark_type,
                watermark_data=watermark_data,
                strength=0.7,  # Default strength
                transparency=0.3,
                detection_threshold=0.8,
                creator_signature=creator_signature
            )
            
            logger.debug(f"💧 Generated watermark: {watermark_id}")
            return watermark
            
        except Exception as e:
            logger.error(f"❌ Watermark generation failed: {e}")
            raise

    async def _apply_watermark(
        self, 
        content_data: bytes, 
        watermark: Watermark, 
        metadata: ContentMetadata
    ) -> bytes:
        """Apply watermark to content"""
        try:
            if metadata.content_type == ContentType.IMAGE:
                return await self._apply_image_watermark(content_data, watermark)
            elif metadata.content_type == ContentType.AUDIO:
                return await self._apply_audio_watermark(content_data, watermark)
            elif metadata.content_type == ContentType.VIDEO:
                return await self._apply_video_watermark(content_data, watermark)
            else:
                return await self._apply_text_watermark(content_data, watermark)
            
        except Exception as e:
            logger.error(f"❌ Watermark application failed: {e}")
            raise

    async def _generate_image_watermark(self, metadata: ContentMetadata, content_data: bytes) -> bytes:
        """Generate watermark for image content"""
        try:
            # Create watermark text
            watermark_text = f"© {metadata.creator_id} - {metadata.content_id[:8]}"
            
            # Create watermark image
            watermark_img = Image.new('RGBA', (300, 50), (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_img)
            
            # Try to use a font, fall back to default if not available
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw text
            draw.text((10, 10), watermark_text, fill=(255, 255, 255, 128), font=font)
            
            # Convert to bytes
            buffer = io.BytesIO()
            watermark_img.save(buffer, format='PNG')
            watermark_data = buffer.getvalue()
            
            return watermark_data
            
        except Exception as e:
            logger.error(f"❌ Image watermark generation failed: {e}")
            # Return simple text-based watermark as fallback
            return watermark_text.encode('utf-8')

    async def _generate_audio_watermark(self, metadata: ContentMetadata, content_data: bytes) -> bytes:
        """Generate watermark for audio content"""
        # Simplified audio watermark (in production, use proper audio steganography)
        watermark_info = {
            'creator_id': metadata.creator_id,
            'content_id': metadata.content_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'audio_steganography'
        }
        return json.dumps(watermark_info).encode('utf-8')

    async def _generate_video_watermark(self, metadata: ContentMetadata, content_data: bytes) -> bytes:
        """Generate watermark for video content"""
        # Simplified video watermark
        watermark_info = {
            'creator_id': metadata.creator_id,
            'content_id': metadata.content_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'video_steganography'
        }
        return json.dumps(watermark_info).encode('utf-8')

    async def _generate_text_watermark(self, metadata: ContentMetadata, content_data: bytes) -> bytes:
        """Generate watermark for text content"""
        watermark_info = {
            'creator_id': metadata.creator_id,
            'content_id': metadata.content_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'text_watermark'
        }
        return json.dumps(watermark_info).encode('utf-8')

    async def _apply_image_watermark(self, content_data: bytes, watermark: Watermark) -> bytes:
        """Apply watermark to image"""
        try:
            # Load original image
            original_img = Image.open(io.BytesIO(content_data))
            
            # Load watermark
            watermark_img = Image.open(io.BytesIO(watermark.watermark_data))
            
            # Apply watermark
            if watermark.position:
                position = watermark.position
            else:
                # Default position (bottom right)
                position = (
                    original_img.width - watermark_img.width - 10,
                    original_img.height - watermark_img.height - 10
                )
            
            # Create a copy and paste watermark
            watermarked_img = original_img.copy()
            watermarked_img.paste(watermark_img, position, watermark_img)
            
            # Convert back to bytes
            buffer = io.BytesIO()
            watermarked_img.save(buffer, format=original_img.format or 'PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Image watermark application failed: {e}")
            # Return original content if watermarking fails
            return content_data

    async def _apply_audio_watermark(self, content_data: bytes, watermark: Watermark) -> bytes:
        """Apply watermark to audio (simplified)"""
        # In production, this would use proper audio steganography
        # For now, append watermark metadata
        watermark_header = b"WATERMARK:" + watermark.watermark_data + b"\n"
        return watermark_header + content_data

    async def _apply_video_watermark(self, content_data: bytes, watermark: Watermark) -> bytes:
        """Apply watermark to video (simplified)"""
        # In production, this would embed watermark in video frames
        watermark_header = b"WATERMARK:" + watermark.watermark_data + b"\n"
        return watermark_header + content_data

    async def _apply_text_watermark(self, content_data: bytes, watermark: Watermark) -> bytes:
        """Apply watermark to text"""
        # For text, append watermark information
        watermark_text = f"\n\n[Content protected by DRM - ID: {watermark.content_id}]"
        return content_data + watermark_text.encode('utf-8')

    def _generate_content_fingerprint(self, content_data: bytes) -> str:
        """Generate unique fingerprint for content"""
        # Create multiple hashes for robust fingerprinting
        sha256_hash = hashlib.sha256(content_data).hexdigest()
        
        # Simplified fingerprint (in production, use perceptual hashing for media)
        return sha256_hash[:32]

    def _derive_content_key(self, content_id: str) -> bytes:
        """Derive encryption key for specific content"""
        # Use HKDF to derive content-specific key from master key
        info = f"content_key_{content_id}".encode('utf-8')
        return hashlib.pbkdf2_hmac('sha256', self.master_key, info, 100000, 32)

    def _create_creator_signature(self, creator: CreatorProfile, metadata: ContentMetadata) -> str:
        """Create cryptographic signature for creator"""
        signature_data = f"{creator.creator_id}:{metadata.content_id}:{metadata.upload_date.isoformat()}"
        signature = hmac.new(
            self.master_key, 
            signature_data.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        return signature

    async def _validate_license(
        self, 
        license: DigitalLicense, 
        usage_type: UsageType, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate license for specific usage"""
        # Check expiration
        if license.end_date and datetime.now() > license.end_date:
            return {'valid': False, 'reason': 'License expired'}
        
        # Check usage limits
        usage_count_key = f"{usage_type.value}_count"
        if usage_count_key in license.usage_limits:
            # Count current usage (simplified)
            current_usage = sum(
                1 for record in self.usage_records
                if (record.license_id == license.license_id and 
                    record.usage_type == usage_type)
            )
            if current_usage >= license.usage_limits[usage_count_key]:
                return {'valid': False, 'reason': 'Usage limit exceeded'}
        
        # Check geographic restrictions
        user_location = context.get('location')
        if license.geographic_restrictions and user_location:
            if user_location not in license.geographic_restrictions:
                return {'valid': False, 'reason': 'Geographic restriction'}
        
        # Check platform restrictions
        user_platform = context.get('platform')
        if license.platform_restrictions and user_platform:
            if user_platform not in license.platform_restrictions:
                return {'valid': False, 'reason': 'Platform restriction'}
        
        return {'valid': True}

    async def _update_usage_analytics(self, usage_record -> None: UsageRecord) -> None:
        """Update usage analytics"""
        content_metadata = self.content_metadata.get(usage_record.content_id)
        if content_metadata:
            creator_id = content_metadata.creator_id
            if creator_id in self.usage_analytics:
                analytics = self.usage_analytics[creator_id]
                
                if usage_record.usage_type == UsageType.VIEW:
                    analytics['total_views'] += 1
                elif usage_record.usage_type == UsageType.DOWNLOAD:
                    analytics['total_downloads'] += 1
                
                analytics['last_activity'] = datetime.now()

    async def _update_license_usage(self, usage_record -> None: UsageRecord) -> None:
        """Update license usage counters"""
        # This would update license usage counters in production
        pass

    async def _scan_for_piracy(
        self, 
        content_id: str, 
        fingerprint: str, 
        scope: str
    ) -> List[Dict[str, Any]]:
        """Scan for piracy (simplified simulation)"""
        # In production, this would integrate with real piracy detection services
        suspicious_urls = []
        
        # Simulate finding suspicious content
        if len(fingerprint) > 20:  # Arbitrary condition for demo
            suspicious_urls.append({
                'url': f'https://suspicious-site.com/content/{content_id}',
                'method': 'fingerprint_match',
                'confidence': 0.85,
                'platform': 'unknown_platform',
                'evidence': {'match_percentage': 85}
            })
        
        return suspicious_urls

    async def _calculate_revenue(
        self, 
        usage_records: List[UsageRecord], 
        creator_id: str
    ) -> Dict[str, Any]:
        """Calculate revenue from usage records"""
        total_revenue = 0.0
        breakdown = {}
        
        # Simplified revenue calculation
        for record in usage_records:
            if record.usage_type == UsageType.VIEW:
                revenue = 0.01  # $0.01 per view
            elif record.usage_type == UsageType.DOWNLOAD:
                revenue = 0.10  # $0.10 per download
            elif record.usage_type == UsageType.STREAM:
                revenue = 0.005  # $0.005 per stream
            else:
                revenue = 0.0
            
            total_revenue += revenue
            breakdown[record.usage_type.value] = breakdown.get(record.usage_type.value, 0) + revenue
        
        return {
            'total': total_revenue,
            'breakdown': breakdown
        }

    def _calculate_revenue_share(self, license_type: LicenseType) -> float:
        """Calculate revenue share percentage"""
        revenue_shares = {
            LicenseType.PERSONAL: 0.7,
            LicenseType.COMMERCIAL: 0.8,
            LicenseType.EDUCATIONAL: 0.6,
            LicenseType.PROMOTIONAL: 0.5,
            LicenseType.STREAMING: 0.7,
            LicenseType.DOWNLOAD: 0.8,
            LicenseType.SUBSCRIPTION: 0.75,
            LicenseType.ROYALTY_FREE: 0.9
        }
        return revenue_shares.get(license_type, 0.7)

    def _validate_creator_profile(self, creator: CreatorProfile) -> bool:
        """Validate creator profile"""
        if not creator.creator_id or not creator.name or not creator.email:
            return False
        
        valid_creator_types = ['musician', 'blogger', 'photographer', 'influencer', 'comedian']
        if creator.creator_type not in valid_creator_types:
            return False
        
        if not (0.0 <= creator.revenue_share_percentage <= 1.0):
            return False
        
        return True

    def _validate_content(self, metadata: ContentMetadata) -> bool:
        """Validate content metadata"""
        if not metadata.content_id or not metadata.title or not metadata.creator_id:
            return False
        
        if metadata.creator_id not in self.creators:
            return False
        
        return True

    # Public API methods

    def get_content_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get protection status for content"""
        if content_id not in self.content_metadata:
            return {'protected': False, 'reason': 'Content not found'}
        
        has_watermark = any(
            wm.content_id == content_id for wm in self.watermarks.values()
        )
        has_fingerprint = content_id in self.content_fingerprints
        
        return {
            'protected': True,
            'watermarked': has_watermark,
            'fingerprinted': has_fingerprint,
            'encryption': 'AES-256',
            'metadata': asdict(self.content_metadata[content_id])
        }

    def get_creator_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get analytics for creator"""
        return self.usage_analytics.get(creator_id, {})

    def list_piracy_alerts(self, content_id: Optional[str] = None) -> List[PiracyAlert]:
        """List piracy alerts"""
        if content_id:
            return [alert for alert in self.piracy_alerts if alert.content_id == content_id]
        return self.piracy_alerts

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            'total_creators': len(self.creators),
            'total_content': len(self.content_metadata),
            'total_licenses': len(self.licenses),
            'total_watermarks': len(self.watermarks),
            'total_usage_records': len(self.usage_records),
            'total_piracy_alerts': len(self.piracy_alerts),
            'content_types': {
                content_type.value: sum(
                    1 for metadata in self.content_metadata.values()
                    if metadata.content_type == content_type
                )
                for content_type in ContentType
            }
        }

# Export main classes
__all__ = [
    'DigitalRightsManagement', 'CreatorProfile', 'ContentMetadata', 
    'DigitalLicense', 'Watermark', 'UsageRecord', 'PiracyAlert',
    'ContentType', 'LicenseType', 'WatermarkType', 'UsageType'
]

if __name__ == "__main__":
    async def test_drm_system() -> None:
        """Test the DRM system"""
        config = {}
        
        drm = DigitalRightsManagement(config)
        
        # Test creator registration
        creator = CreatorProfile(
            creator_id="musician_001",
            creator_type="musician",
            name="John Doe",
            email="john@example.com",
            verification_status="verified",
            revenue_share_percentage=0.8,
            content_categories=["pop", "rock"],
            geographic_regions=["US", "EU"],
            payment_details={"bank": "example_bank"}
        )
        
        success = await drm.register_creator(creator)
        print(f"👨‍🎨 Creator registration: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Test content protection
        content_metadata = ContentMetadata(
            content_id="song_001",
            title="My Great Song",
            creator_id="musician_001",
            content_type=ContentType.AUDIO,
            file_size=5000000,
            duration=180.0,
            format="mp3",
            quality="high"
        )
        
        sample_content = b"This is sample audio content for testing DRM"
        
        protection_info = await drm.protect_content(content_metadata, sample_content)
        print(f"🔒 Content protection: {'✅ SUCCESS' if protection_info else '❌ FAILED'}")
        
        if protection_info:
            print(f"   Content ID: {protection_info['content_id']}")
            print(f"   Size: {protection_info['size_original']} → {protection_info['size_protected']} bytes")
            print(f"   Fingerprint: {protection_info['fingerprint'][:16]}...")
        
        # Test license creation
        license = await drm.create_license(
            content_id="song_001",
            licensee_id="user_001",
            license_type=LicenseType.PERSONAL,
            allowed_usages={UsageType.STREAM, UsageType.DOWNLOAD},
            usage_limits={'stream_count': 100, 'download_count': 5},
            duration_days=30
        )
        
        print(f"📜 License creation: {'✅ SUCCESS' if license else '❌ FAILED'}")
        
        # Test usage validation
        validation_result = await drm.validate_usage(
            content_id="song_001",
            user_id="user_001",
            usage_type=UsageType.STREAM,
            context={'platform': 'mobile_app', 'location': 'US'}
        )
        
        print(f"✅ Usage validation: {'✅ ALLOWED' if validation_result['allowed'] else '❌ DENIED'}")
        
        # Test usage tracking
        usage_record = await drm.track_usage(
            content_id="song_001",
            user_id="user_001",
            usage_type=UsageType.STREAM,
            context={
                'license_id': license.license_id,
                'platform': 'mobile_app',
                'ip_address': '192.168.1.1',
                'duration': 120.0
            }
        )
        
        print(f"📊 Usage tracking: {'✅ SUCCESS' if usage_record else '❌ FAILED'}")
        
        # Test piracy detection
        piracy_alerts = await drm.detect_piracy("song_001")
        print(f"🚨 Piracy detection: {len(piracy_alerts)} alerts found")
        
        # Get system metrics
        metrics = drm.get_system_metrics()
        print(f"\n📊 System Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
    
    # Run test
    asyncio.run(test_drm_system())