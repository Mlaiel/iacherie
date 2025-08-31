"""Watermark Metadata Management System
Professional metadata handling for digital watermarking operations

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This watermark metadata system, concept, and all associated code are the exclusive intellectual 
property of Fahed Mlaiel. Any unauthorized use, copying, modification, or distribution 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly 
prohibited and will result in legal action.
"""import asyncio
import logging
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
from pathlib import Path
import mimetypes
import os

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Content categories for watermarking"""    MUSIC_TRACK = "music_track"
    PODCAST_EPISODE = "podcast_episode"
    VOICE_RECORDING = "voice_recording"
    SOUND_EFFECT = "sound_effect"
    PHOTOGRAPH = "photograph"
    DIGITAL_ART = "digital_art"
    GRAPHIC_DESIGN = "graphic_design"
    VIDEO_CONTENT = "video_content"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    TEXT_ARTICLE = "text_article"
    BLOG_POST = "blog_post"
    EBOOK = "ebook"
    SCRIPT = "script"
    OTHER = "other"


class LicenseType(Enum):
    """License types for content"""    ALL_RIGHTS_RESERVED = "all_rights_reserved"
    CREATIVE_COMMONS_BY = "cc_by"
    CREATIVE_COMMONS_SA = "cc_sa"
    CREATIVE_COMMONS_NC = "cc_nc"
    CREATIVE_COMMONS_ND = "cc_nd"
    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE_LICENSE = "exclusive_license"
    NON_EXCLUSIVE_LICENSE = "non_exclusive_license"
    CUSTOM_LICENSE = "custom_license"


class WatermarkPurpose(Enum):
    """Purpose of watermarking"""    COPYRIGHT_PROTECTION = "copyright_protection"
    OWNERSHIP_VERIFICATION = "ownership_verification"
    USAGE_TRACKING = "usage_tracking"
    ANTI_PIRACY = "anti_piracy"
    BROADCAST_MONITORING = "broadcast_monitoring"
    CONTENT_AUTHENTICATION = "content_authentication"
    REVENUE_TRACKING = "revenue_tracking"
    DISTRIBUTION_CONTROL = "distribution_control"


class WatermarkStatus(Enum):
    """Watermark processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    COMPROMISED = "compromised"
    REMOVED = "removed"


@dataclass
class ContentIdentification:
    """Content identification information"""    content_id: str
    title: str
    category: ContentCategory
    mime_type: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    color_depth: Optional[int] = None
    language: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentIdentification':
        """Create from dictionary"""        if 'category' in data and isinstance(data['category'], str):
            data['category'] = ContentCategory(data['category'])
        return cls(**data)


@dataclass
class OwnershipInfo:
    """Content ownership information"""    owner_id: str
    owner_name: str
    owner_email: str
    organization: Optional[str] = None
    country: Optional[str] = None
    registration_number: Optional[str] = None
    copyright_year: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OwnershipInfo':
        """Create from dictionary"""        return cls(**data)


@dataclass
class LicensingInfo:
    """Content licensing information"""    license_type: LicenseType
    license_url: Optional[str] = None
    usage_restrictions: List[str] = None
    commercial_use_allowed: bool = False
    modification_allowed: bool = False
    redistribution_allowed: bool = False
    attribution_required: bool = True
    license_expiry: Optional[datetime] = None
    custom_terms: Optional[str] = None
    
    def __post_init__(self):
        if self.usage_restrictions is None:
            self.usage_restrictions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['license_type'] = self.license_type.value
        if self.license_expiry:
            data['license_expiry'] = self.license_expiry.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LicensingInfo':
        """Create from dictionary"""        if 'license_type' in data and isinstance(data['license_type'], str):
            data['license_type'] = LicenseType(data['license_type'])
        if 'license_expiry' in data and isinstance(data['license_expiry'], str):
            data['license_expiry'] = datetime.fromisoformat(data['license_expiry'])
        return cls(**data)


@dataclass
class WatermarkTechnicalInfo:
    """Technical watermarking information"""    watermark_id: str
    technique_used: str
    strength_level: str
    embedding_timestamp: datetime
    embedding_duration_seconds: float
    bits_embedded: int
    redundancy_factor: int
    error_correction_enabled: bool
    encryption_enabled: bool
    frequency_range: Optional[Tuple[float, float]] = None
    spatial_region: Optional[Tuple[int, int, int, int]] = None
    quality_metrics: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['embedding_timestamp'] = self.embedding_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WatermarkTechnicalInfo':
        """Create from dictionary"""        if 'embedding_timestamp' in data and isinstance(data['embedding_timestamp'], str):
            data['embedding_timestamp'] = datetime.fromisoformat(data['embedding_timestamp'])
        return cls(**data)


@dataclass
class TrackingInfo:
    """Content tracking and monitoring information"""    tracking_id: str
    monitoring_enabled: bool
    last_detection: Optional[datetime] = None
    detection_count: int = 0
    unauthorized_usage_count: int = 0
    platforms_detected: List[str] = None
    geographic_usage: Dict[str, int] = None
    revenue_tracked: float = 0.0
    last_verification: Optional[datetime] = None
    
    def __post_init__(self):
        if self.platforms_detected is None:
            self.platforms_detected = []
        if self.geographic_usage is None:
            self.geographic_usage = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        if self.last_detection:
            data['last_detection'] = self.last_detection.isoformat()
        if self.last_verification:
            data['last_verification'] = self.last_verification.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackingInfo':
        """Create from dictionary"""        if 'last_detection' in data and isinstance(data['last_detection'], str):
            data['last_detection'] = datetime.fromisoformat(data['last_detection'])
        if 'last_verification' in data and isinstance(data['last_verification'], str):
            data['last_verification'] = datetime.fromisoformat(data['last_verification'])
        return cls(**data)


@dataclass
class WatermarkMetadata:
    """Complete watermark metadata package"""    
    # Core identification
    metadata_id: str
    version: str
    created_at: datetime
    updated_at: datetime
    status: WatermarkStatus
    
    # Content information
    content_info: ContentIdentification
    ownership_info: OwnershipInfo
    licensing_info: LicensingInfo
    
    # Technical details
    technical_info: WatermarkTechnicalInfo
    tracking_info: TrackingInfo
    
    # Additional metadata
    purpose: WatermarkPurpose
    tags: List[str]
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = None
    
    # File paths
    original_file_path: Optional[str] = None
    watermarked_file_path: Optional[str] = None
    backup_file_path: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete metadata to dictionary"""        return {
            'metadata_id': self.metadata_id,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'content_info': self.content_info.to_dict(),
            'ownership_info': self.ownership_info.to_dict(),
            'licensing_info': self.licensing_info.to_dict(),
            'technical_info': self.technical_info.to_dict(),
            'tracking_info': self.tracking_info.to_dict(),
            'purpose': self.purpose.value,
            'tags': self.tags,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'original_file_path': self.original_file_path,
            'watermarked_file_path': self.watermarked_file_path,
            'backup_file_path': self.backup_file_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WatermarkMetadata':
        """Create metadata from dictionary"""        # Convert enum fields
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = WatermarkStatus(data['status'])
        if 'purpose' in data and isinstance(data['purpose'], str):
            data['purpose'] = WatermarkPurpose(data['purpose'])
        
        # Convert datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert nested objects
        if 'content_info' in data:
            data['content_info'] = ContentIdentification.from_dict(data['content_info'])
        if 'ownership_info' in data:
            data['ownership_info'] = OwnershipInfo.from_dict(data['ownership_info'])
        if 'licensing_info' in data:
            data['licensing_info'] = LicensingInfo.from_dict(data['licensing_info'])
        if 'technical_info' in data:
            data['technical_info'] = WatermarkTechnicalInfo.from_dict(data['technical_info'])
        if 'tracking_info' in data:
            data['tracking_info'] = TrackingInfo.from_dict(data['tracking_info'])
        
        return cls(**data)
    
    def update_status(self, new_status: WatermarkStatus, notes: Optional[str] = None):
        """Update status with timestamp"""        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        if notes:
            if self.notes:
                self.notes += f"\n{datetime.now().isoformat()}: {notes}"
            else:
                self.notes = f"{datetime.now().isoformat()}: {notes}"
    
    def add_detection(self, platform: str, location: Optional[str] = None):
        """Add detection event"""        self.tracking_info.detection_count += 1
        self.tracking_info.last_detection = datetime.now(timezone.utc)
        
        if platform not in self.tracking_info.platforms_detected:
            self.tracking_info.platforms_detected.append(platform)
        
        if location:
            if location in self.tracking_info.geographic_usage:
                self.tracking_info.geographic_usage[location] += 1
            else:
                self.tracking_info.geographic_usage[location] = 1
        
        self.updated_at = datetime.now(timezone.utc)
    
    def add_revenue(self, amount: float, currency: str = "USD"):
        """Add revenue tracking"""        self.tracking_info.revenue_tracked += amount
        self.updated_at = datetime.now(timezone.utc)
        
        # Add to custom fields if currency tracking needed
        if 'revenue_by_currency' not in self.custom_fields:
            self.custom_fields['revenue_by_currency'] = {}
        
        if currency in self.custom_fields['revenue_by_currency']:
            self.custom_fields['revenue_by_currency'][currency] += amount
        else:
            self.custom_fields['revenue_by_currency'][currency] = amount
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metadata summary"""        return {
            'metadata_id': self.metadata_id,
            'content_title': self.content_info.title,
            'owner_name': self.ownership_info.owner_name,
            'status': self.status.value,
            'watermark_technique': self.technical_info.technique_used,
            'detection_count': self.tracking_info.detection_count,
            'revenue_tracked': self.tracking_info.revenue_tracked,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.updated_at.isoformat()
        }


class MetadataEncryption:
    """Encryption service for sensitive metadata"""    
    def __init__(self, encryption_key: Optional[bytes] = None):
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available - encryption disabled")
            self.encryption_enabled = False
            return
        
        self.encryption_enabled = True
        
        if encryption_key:
            self.key = encryption_key
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def encrypt_metadata(self, metadata_dict: Dict[str, Any]) -> bytes:
        """Encrypt metadata dictionary"""        if not self.encryption_enabled:
            return json.dumps(metadata_dict).encode('utf-8')
        
        try:
            json_data = json.dumps(metadata_dict, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            return encrypted_data
        except Exception as e:
            logger.error(f"Error encrypting metadata: {e}")
            raise
    
    def decrypt_metadata(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt metadata"""        if not self.encryption_enabled:
            return json.loads(encrypted_data.decode('utf-8'))
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            metadata_dict = json.loads(decrypted_data.decode('utf-8'))
            return metadata_dict
        except Exception as e:
            logger.error(f"Error decrypting metadata: {e}")
            raise
    
    def get_key(self) -> bytes:
        """Get encryption key"""        return self.key if self.encryption_enabled else b''


class WatermarkMetadataManager:
    """    Professional Watermark Metadata Management System
    
    Handles creation, storage, retrieval, and management of watermark metadata
    with encryption, versioning, and comprehensive tracking capabilities.
    """    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 encryption_enabled: bool = True,
                 encryption_key: Optional[bytes] = None):
        self.storage_path = Path(storage_path) if storage_path else Path.cwd() / 'watermark_metadata'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.encryption = MetadataEncryption(encryption_key) if encryption_enabled else None
        self.metadata_cache: Dict[str, WatermarkMetadata] = {}
        self.index_file = self.storage_path / 'metadata_index.json'
        
        # Initialize index
        self._load_index()
    
    def _load_index(self):
        """Load metadata index"""        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            else:
                self.index = {}
        except Exception as e:
            logger.error(f"Error loading metadata index: {e}")
            self.index = {}
    
    def _save_index(self):
        """Save metadata index"""        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving metadata index: {e}")
    
    async def create_metadata(self,
                            content_info: ContentIdentification,
                            ownership_info: OwnershipInfo,
                            licensing_info: LicensingInfo,
                            technical_info: WatermarkTechnicalInfo,
                            purpose: WatermarkPurpose,
                            tags: Optional[List[str]] = None,
                            notes: Optional[str] = None) -> WatermarkMetadata:
        """Create new watermark metadata"""        try:
            # Generate unique ID
            metadata_id = str(uuid.uuid4())
            tracking_id = str(uuid.uuid4())
            
            # Create tracking info
            tracking_info = TrackingInfo(
                tracking_id=tracking_id,
                monitoring_enabled=True
            )
            
            # Create metadata object
            metadata = WatermarkMetadata(
                metadata_id=metadata_id,
                version="1.0",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                status=WatermarkStatus.PENDING,
                content_info=content_info,
                ownership_info=ownership_info,
                licensing_info=licensing_info,
                technical_info=technical_info,
                tracking_info=tracking_info,
                purpose=purpose,
                tags=tags or [],
                notes=notes
            )
            
            # Save metadata
            await self.save_metadata(metadata)
            
            logger.info(f"Created metadata for content: {content_info.title}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating metadata: {e}")
            raise
    
    async def save_metadata(self, metadata: WatermarkMetadata) -> bool:
        """Save metadata to storage"""        try:
            # Update timestamp
            metadata.updated_at = datetime.now(timezone.utc)
            
            # Convert to dictionary
            metadata_dict = metadata.to_dict()
            
            # Encrypt if enabled
            if self.encryption:
                data = self.encryption.encrypt_metadata(metadata_dict)
                file_extension = '.enc'
            else:
                data = json.dumps(metadata_dict, indent=2, ensure_ascii=False).encode('utf-8')
                file_extension = '.json'
            
            # Save to file
            metadata_file = self.storage_path / f"{metadata.metadata_id}{file_extension}"
            with open(metadata_file, 'wb') as f:
                f.write(data)
            
            # Update index
            self.index[metadata.metadata_id] = {
                'file_path': str(metadata_file),
                'content_title': metadata.content_info.title,
                'owner_name': metadata.ownership_info.owner_name,
                'status': metadata.status.value,
                'created_at': metadata.created_at.isoformat(),
                'updated_at': metadata.updated_at.isoformat(),
                'encrypted': self.encryption is not None
            }
            
            self._save_index()
            
            # Cache metadata
            self.metadata_cache[metadata.metadata_id] = metadata
            
            logger.info(f"Saved metadata: {metadata.metadata_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False
    
    async def load_metadata(self, metadata_id: str) -> Optional[WatermarkMetadata]:
        """Load metadata from storage"""        try:
            # Check cache first
            if metadata_id in self.metadata_cache:
                return self.metadata_cache[metadata_id]
            
            # Check index
            if metadata_id not in self.index:
                logger.warning(f"Metadata not found in index: {metadata_id}")
                return None
            
            # Load from file
            metadata_info = self.index[metadata_id]
            metadata_file = Path(metadata_info['file_path'])
            
            if not metadata_file.exists():
                logger.error(f"Metadata file not found: {metadata_file}")
                return None
            
            # Read file
            with open(metadata_file, 'rb') as f:
                data = f.read()
            
            # Decrypt if needed
            if metadata_info.get('encrypted', False) and self.encryption:
                metadata_dict = self.encryption.decrypt_metadata(data)
            else:
                metadata_dict = json.loads(data.decode('utf-8'))
            
            # Create metadata object
            metadata = WatermarkMetadata.from_dict(metadata_dict)
            
            # Cache metadata
            self.metadata_cache[metadata_id] = metadata
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error loading metadata {metadata_id}: {e}")
            return None
    
    async def update_metadata(self, metadata_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing metadata"""        try:
            metadata = await self.load_metadata(metadata_id)
            if not metadata:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
                else:
                    # Add to custom fields
                    metadata.custom_fields[key] = value
            
            # Save updated metadata
            return await self.save_metadata(metadata)
            
        except Exception as e:
            logger.error(f"Error updating metadata {metadata_id}: {e}")
            return False
    
    async def delete_metadata(self, metadata_id: str) -> bool:
        """Delete metadata"""        try:
            # Check if exists
            if metadata_id not in self.index:
                return False
            
            # Remove file
            metadata_info = self.index[metadata_id]
            metadata_file = Path(metadata_info['file_path'])
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Remove from index
            del self.index[metadata_id]
            self._save_index()
            
            # Remove from cache
            if metadata_id in self.metadata_cache:
                del self.metadata_cache[metadata_id]
            
            logger.info(f"Deleted metadata: {metadata_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting metadata {metadata_id}: {e}")
            return False
    
    async def search_metadata(self, 
                            query: Optional[str] = None,
                            owner_id: Optional[str] = None,
                            status: Optional[WatermarkStatus] = None,
                            purpose: Optional[WatermarkPurpose] = None,
                            category: Optional[ContentCategory] = None,
                            tags: Optional[List[str]] = None,
                            date_from: Optional[datetime] = None,
                            date_to: Optional[datetime] = None) -> List[WatermarkMetadata]:
        """Search metadata with various filters"""        try:
            results = []
            
            for metadata_id, index_info in self.index.items():
                # Load metadata for detailed search
                metadata = await self.load_metadata(metadata_id)
                if not metadata:
                    continue
                
                # Apply filters
                matches = True
                
                if query:
                    # Text search in title, notes, tags
                    search_text = (
                        metadata.content_info.title.lower() + " " +
                        (metadata.notes or "").lower() + " " +
                        " ".join(metadata.tags).lower()
                    )
                    if query.lower() not in search_text:
                        matches = False
                
                if owner_id and metadata.ownership_info.owner_id != owner_id:
                    matches = False
                
                if status and metadata.status != status:
                    matches = False
                
                if purpose and metadata.purpose != purpose:
                    matches = False
                
                if category and metadata.content_info.category != category:
                    matches = False
                
                if tags:
                    if not any(tag in metadata.tags for tag in tags):
                        matches = False
                
                if date_from and metadata.created_at < date_from:
                    matches = False
                
                if date_to and metadata.created_at > date_to:
                    matches = False
                
                if matches:
                    results.append(metadata)
            
            logger.info(f"Found {len(results)} matching metadata records")
            return results
            
        except Exception as e:
            logger.error(f"Error searching metadata: {e}")
            return []
    
    async def get_metadata_summary(self) -> Dict[str, Any]:
        """Get overall metadata statistics"""        try:
            total_records = len(self.index)
            status_counts = {}
            category_counts = {}
            purpose_counts = {}
            
            for metadata_id in self.index.keys():
                metadata = await self.load_metadata(metadata_id)
                if metadata:
                    # Count by status
                    status = metadata.status.value
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Count by category
                    category = metadata.content_info.category.value
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    # Count by purpose
                    purpose = metadata.purpose.value
                    purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
            
            return {
                'total_records': total_records,
                'status_distribution': status_counts,
                'category_distribution': category_counts,
                'purpose_distribution': purpose_counts,
                'storage_path': str(self.storage_path),
                'encryption_enabled': self.encryption is not None
            }
            
        except Exception as e:
            logger.error(f"Error generating metadata summary: {e}")
            return {}
    
    async def export_metadata(self, 
                            metadata_ids: Optional[List[str]] = None,
                            export_format: str = 'json',
                            include_sensitive: bool = False) -> Optional[bytes]:
        """Export metadata to various formats"""        try:
            # Determine which metadata to export
            if metadata_ids:
                metadatas = []
                for metadata_id in metadata_ids:
                    metadata = await self.load_metadata(metadata_id)
                    if metadata:
                        metadatas.append(metadata)
            else:
                # Export all
                metadatas = []
                for metadata_id in self.index.keys():
                    metadata = await self.load_metadata(metadata_id)
                    if metadata:
                        metadatas.append(metadata)
            
            # Convert to export format
            export_data = []
            for metadata in metadatas:
                metadata_dict = metadata.to_dict()
                
                # Remove sensitive information if requested
                if not include_sensitive:
                    # Remove owner email, encryption keys, etc.
                    if 'ownership_info' in metadata_dict:
                        metadata_dict['ownership_info'].pop('owner_email', None)
                    if 'technical_info' in metadata_dict:
                        metadata_dict['technical_info'].pop('encryption_key', None)
                
                export_data.append(metadata_dict)
            
            # Format output
            if export_format.lower() == 'json':
                output = json.dumps({
                    'export_timestamp': datetime.now(timezone.utc).isoformat(),
                    'metadata_count': len(export_data),
                    'metadata': export_data
                }, indent=2, ensure_ascii=False)
                return output.encode('utf-8')
            
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
        except Exception as e:
            logger.error(f"Error exporting metadata: {e}")
            return None
    
    async def backup_metadata(self, backup_path: Optional[str] = None) -> bool:
        """Create backup of all metadata"""        try:
            if not backup_path:
                backup_path = self.storage_path.parent / f"watermark_metadata_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all metadata files
            import shutil
            for metadata_id, info in self.index.items():
                source_file = Path(info['file_path'])
                if source_file.exists():
                    target_file = backup_dir / source_file.name
                    shutil.copy2(source_file, target_file)
            
            # Copy index file
            shutil.copy2(self.index_file, backup_dir / 'metadata_index.json')
            
            logger.info(f"Metadata backup created: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating metadata backup: {e}")
            return False
    
    def get_encryption_key(self) -> Optional[bytes]:
        """Get encryption key for backup purposes"""        if self.encryption:
            return self.encryption.get_key()
        return None


# Utility functions for metadata creation

def create_content_info_from_file(file_path: str, 
                                title: Optional[str] = None,
                                category: Optional[ContentCategory] = None) -> ContentIdentification:
    """Create content identification from file"""    file_path = Path(file_path)
    
    # Auto-detect MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "application/octet-stream"
    
    # Get file size
    file_size = file_path.stat().st_size if file_path.exists() else 0
    
    # Auto-detect category if not provided
    if not category:
        if mime_type.startswith('audio/'):
            category = ContentCategory.MUSIC_TRACK
        elif mime_type.startswith('image/'):
            category = ContentCategory.PHOTOGRAPH
        elif mime_type.startswith('video/'):
            category = ContentCategory.VIDEO_CONTENT
        elif mime_type.startswith('text/'):
            category = ContentCategory.TEXT_ARTICLE
        else:
            category = ContentCategory.OTHER
    
    return ContentIdentification(
        content_id=str(uuid.uuid4()),
        title=title or file_path.stem,
        category=category,
        mime_type=mime_type,
        file_size_bytes=file_size
    )


def create_basic_ownership_info(owner_name: str, 
                              owner_email: str,
                              organization: Optional[str] = None) -> OwnershipInfo:
    """Create basic ownership information"""    return OwnershipInfo(
        owner_id=str(uuid.uuid4()),
        owner_name=owner_name,
        owner_email=owner_email,
        organization=organization,
        copyright_year=datetime.now().year
    )


def create_standard_licensing_info(license_type: LicenseType = LicenseType.ALL_RIGHTS_RESERVED) -> LicensingInfo:
    """Create standard licensing information"""    return LicensingInfo(
        license_type=license_type,
        commercial_use_allowed=(license_type != LicenseType.ALL_RIGHTS_RESERVED),
        modification_allowed=(license_type in [LicenseType.CREATIVE_COMMONS_BY, LicenseType.CREATIVE_COMMONS_SA]),
        redistribution_allowed=(license_type != LicenseType.ALL_RIGHTS_RESERVED),
        attribution_required=True
    )


# Factory function
def create_metadata_manager(storage_path: Optional[str] = None,
                          encryption_enabled: bool = True) -> WatermarkMetadataManager:
    """Create metadata manager with standard configuration"""    return WatermarkMetadataManager(
        storage_path=storage_path,
        encryption_enabled=encryption_enabled
    )


__all__ = [
    'WatermarkMetadataManager',
    'WatermarkMetadata',
    'ContentIdentification',
    'OwnershipInfo',
    'LicensingInfo',
    'WatermarkTechnicalInfo',
    'TrackingInfo',
    'MetadataEncryption',
    'ContentCategory',
    'LicenseType',
    'WatermarkPurpose',
    'WatermarkStatus',
    'create_content_info_from_file',
    'create_basic_ownership_info',
    'create_standard_licensing_info',
    'create_metadata_manager'
]
