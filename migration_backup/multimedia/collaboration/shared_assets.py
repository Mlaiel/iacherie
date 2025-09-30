"""
Ainflue Platform - Multimedia Collaboration - Shared Assets Management
Professional shared multimedia assets and resource management for teams

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Shared asset types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FONT = "font"
    TEMPLATE = "template"
    PRESET = "preset"
    EFFECT = "effect"
    TEXTURE = "texture"
    MODEL_3D = "model_3d"
    ANIMATION = "animation"
    DOCUMENT = "document"
    ARCHIVE = "archive"


class AssetCategory(Enum):
    """Asset categories for organization"""
    BACKGROUNDS = "backgrounds"
    OVERLAYS = "overlays"
    TRANSITIONS = "transitions"
    EFFECTS = "effects"
    MUSIC = "music"
    SOUND_EFFECTS = "sound_effects"
    TEMPLATES = "templates"
    FONTS = "fonts"
    LOGOS = "logos"
    ICONS = "icons"
    TEXTURES = "textures"
    MODELS = "models"
    PRESETS = "presets"


class AccessLevel(Enum):
    """Asset access levels"""
    PUBLIC = "public"           # Everyone can view and use
    TEAM_READ = "team_read"     # Team can view and use
    TEAM_EDIT = "team_edit"     # Team can view, use, and edit
    RESTRICTED = "restricted"    # Limited access list
    PRIVATE = "private"         # Owner only


class AssetStatus(Enum):
    """Asset status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


@dataclass
class AssetVersion:
    """Asset version information"""
    version: str = "1.0.0"
    created_at: Optional[float] = None
    created_by: str = ""
    changelog: str = ""
    file_path: str = ""
    file_hash: str = ""
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()


@dataclass
class AssetMetadata:
    """Comprehensive asset metadata"""
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    category: Optional[AssetCategory] = None
    resolution: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    format: str = ""
    color_space: str = ""
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    license: str = ""
    copyright_info: str = ""
    usage_rights: str = ""
    attribution_required: bool = False


@dataclass
class SharedAsset:
    """Shared multimedia asset"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: AssetType = AssetType.IMAGE
    name: str = ""
    owner_id: str = ""
    team_id: Optional[str] = None
    access_level: AccessLevel = AccessLevel.TEAM_READ
    status: AssetStatus = AssetStatus.DRAFT
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    versions: List[AssetVersion] = field(default_factory=list)
    current_version: str = "1.0.0"
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    downloads: int = 0
    usage_count: int = 0
    favorites: int = 0
    ratings: List[float] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    authorized_users: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class AssetCollection:
    """Collection of related assets"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    owner_id: str = ""
    team_id: Optional[str] = None
    asset_ids: List[str] = field(default_factory=list)
    public: bool = False
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class AssetUsage:
    """Asset usage tracking"""
    asset_id: str = ""
    user_id: str = ""
    project_id: Optional[str] = None
    used_at: Optional[float] = None
    usage_context: str = ""  # "video_edit", "image_composite", etc.
    
    def __post_init__(self):
        if self.used_at is None:
            self.used_at = datetime.now().timestamp()


class SharedAssetsManager:
    """Professional shared multimedia assets management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize shared assets manager"""
        self.config = config or {}
        self.assets: Dict[str, SharedAsset] = {}
        self.collections: Dict[str, AssetCollection] = {}
        self.usage_history: List[AssetUsage] = []
        self.storage_path = Path(self.config.get('storage_path', '/tmp/shared_assets'))
        self.max_file_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self.supported_formats = self.config.get('supported_formats', {
            AssetType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
            AssetType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'],
            AssetType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            AssetType.FONT: ['.ttf', '.otf', '.woff', '.woff2'],
            AssetType.TEMPLATE: ['.json', '.xml', '.psd', '.ai'],
            AssetType.PRESET: ['.json', '.xml'],
            AssetType.EFFECT: ['.json', '.fx'],
            AssetType.TEXTURE: ['.jpg', '.png', '.tiff', '.exr', '.hdr'],
            AssetType.MODEL_3D: ['.obj', '.fbx', '.gltf', '.glb', '.3ds'],
            AssetType.ANIMATION: ['.gif', '.lottie', '.json'],
            AssetType.DOCUMENT: ['.pdf', '.doc', '.docx', '.txt', '.md'],
            AssetType.ARCHIVE: ['.zip', '.rar', '.7z', '.tar', '.gz']
        })
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_asset(
        self,
        file_data: bytes,
        filename: str,
        asset_type: AssetType,
        owner_id: str,
        team_id: Optional[str] = None,
        metadata: Optional[AssetMetadata] = None,
        access_level: AccessLevel = AccessLevel.TEAM_READ
    ) -> SharedAsset:
        """Upload a new shared asset"""
        try:
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed ({self.max_file_size} bytes)")
            
            # Validate file format
            file_extension = Path(filename).suffix.lower()
            if asset_type in self.supported_formats:
                if file_extension not in self.supported_formats[asset_type]:
                    raise ValueError(f"Unsupported file format {file_extension} for {asset_type.value}")
            
            # Generate file hash for deduplication
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Check for existing asset with same hash
            existing_asset = await self._find_asset_by_hash(file_hash)
            if existing_asset:
                logger.info(f"Asset with hash {file_hash} already exists: {existing_asset.id}")
                return existing_asset
            
            # Create asset
            asset = SharedAsset(
                asset_type=asset_type,
                name=Path(filename).stem,
                owner_id=owner_id,
                team_id=team_id,
                access_level=access_level,
                metadata=metadata or AssetMetadata()
            )
            
            # Create first version
            version = AssetVersion(
                version="1.0.0",
                created_by=owner_id,
                file_hash=file_hash,
                size=len(file_data),
                metadata=await self._extract_file_metadata(file_data, filename, asset_type)
            )
            
            # Save file to storage
            asset_dir = self.storage_path / asset.id
            asset_dir.mkdir(exist_ok=True)
            
            version.file_path = str(asset_dir / f"v{version.version}_{filename}")
            
            with open(version.file_path, 'wb') as f:
                f.write(file_data)
            
            asset.versions.append(version)
            self.assets[asset.id] = asset
            
            logger.info(f"Uploaded asset {asset.id}: {filename}")
            return asset
            
        except Exception as e:
            logger.error(f"Error uploading asset: {e}")
            raise
    
    async def update_asset_version(
        self,
        asset_id: str,
        file_data: bytes,
        filename: str,
        user_id: str,
        version: str,
        changelog: str = ""
    ) -> AssetVersion:
        """Update asset with new version"""
        try:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            asset = self.assets[asset_id]
            
            # Check permissions
            if not await self._check_edit_permission(asset, user_id):
                raise ValueError("User not authorized to edit this asset")
            
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed ({self.max_file_size} bytes)")
            
            # Generate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Create new version
            new_version = AssetVersion(
                version=version,
                created_by=user_id,
                changelog=changelog,
                file_hash=file_hash,
                size=len(file_data),
                metadata=await self._extract_file_metadata(file_data, filename, asset.asset_type)
            )
            
            # Save new version file
            asset_dir = self.storage_path / asset.id
            new_version.file_path = str(asset_dir / f"v{version}_{filename}")
            
            with open(new_version.file_path, 'wb') as f:
                f.write(file_data)
            
            asset.versions.append(new_version)
            asset.current_version = version
            asset.updated_at = datetime.now().timestamp()
            
            logger.info(f"Updated asset {asset_id} to version {version}")
            return new_version
            
        except Exception as e:
            logger.error(f"Error updating asset version: {e}")
            raise
    
    async def get_asset(
        self,
        asset_id: str,
        user_id: str,
        version: Optional[str] = None
    ) -> Optional[Tuple[SharedAsset, bytes]]:
        """Get asset data and content"""
        try:
            if asset_id not in self.assets:
                return None
            
            asset = self.assets[asset_id]
            
            # Check permissions
            if not await self._check_access_permission(asset, user_id):
                raise ValueError("User not authorized to access this asset")
            
            # Get specified version or current version
            target_version = version or asset.current_version
            asset_version = None
            
            for v in asset.versions:
                if v.version == target_version:
                    asset_version = v
                    break
            
            if not asset_version:
                raise ValueError(f"Version {target_version} not found")
            
            # Read file content
            if not Path(asset_version.file_path).exists():
                raise FileNotFoundError(f"Asset file not found: {asset_version.file_path}")
            
            with open(asset_version.file_path, 'rb') as f:
                file_data = f.read()
            
            # Track usage
            await self._track_usage(asset_id, user_id)
            
            return asset, file_data
            
        except Exception as e:
            logger.error(f"Error getting asset: {e}")
            raise
    
    async def search_assets(
        self,
        user_id: str,
        query: Optional[str] = None,
        asset_type: Optional[AssetType] = None,
        category: Optional[AssetCategory] = None,
        tags: Optional[List[str]] = None,
        team_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SharedAsset]:
        """Search for assets with filters"""
        try:
            results = []
            
            for asset in self.assets.values():
                # Check access permission
                if not await self._check_access_permission(asset, user_id):
                    continue
                
                # Apply filters
                if asset_type and asset.asset_type != asset_type:
                    continue
                
                if category and asset.metadata.category != category:
                    continue
                
                if team_id and asset.team_id != team_id:
                    continue
                
                if tags:
                    if not any(tag in asset.metadata.tags for tag in tags):
                        continue
                
                if query:
                    # Search in name, description, tags, keywords
                    search_text = f"{asset.name} {asset.metadata.description} {' '.join(asset.metadata.tags)} {' '.join(asset.metadata.keywords)}".lower()
                    if query.lower() not in search_text:
                        continue
                
                results.append(asset)
            
            # Sort by relevance/popularity
            results.sort(key=lambda x: (x.usage_count, x.favorites, x.downloads), reverse=True)
            
            # Apply pagination
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            raise
    
    async def create_collection(
        self,
        name: str,
        description: str,
        owner_id: str,
        team_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        public: bool = False
    ) -> AssetCollection:
        """Create a new asset collection"""
        try:
            collection = AssetCollection(
                name=name,
                description=description,
                owner_id=owner_id,
                team_id=team_id,
                asset_ids=asset_ids or [],
                public=public
            )
            
            self.collections[collection.id] = collection
            
            logger.info(f"Created collection {collection.id}: {name}")
            return collection
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def add_asset_to_collection(
        self,
        collection_id: str,
        asset_id: str,
        user_id: str
    ) -> bool:
        """Add asset to collection"""
        try:
            if collection_id not in self.collections:
                raise ValueError(f"Collection {collection_id} not found")
            
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            collection = self.collections[collection_id]
            asset = self.assets[asset_id]
            
            # Check permissions
            if collection.owner_id != user_id and not await self._check_access_permission(asset, user_id):
                raise ValueError("User not authorized to add this asset to collection")
            
            if asset_id not in collection.asset_ids:
                collection.asset_ids.append(asset_id)
                collection.updated_at = datetime.now().timestamp()
            
            logger.info(f"Added asset {asset_id} to collection {collection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding asset to collection: {e}")
            raise
    
    async def favorite_asset(
        self,
        asset_id: str,
        user_id: str
    ) -> bool:
        """Mark asset as favorite"""
        try:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            asset = self.assets[asset_id]
            
            # Check access permission
            if not await self._check_access_permission(asset, user_id):
                raise ValueError("User not authorized to access this asset")
            
            asset.favorites += 1
            logger.info(f"Asset {asset_id} favorited by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error favoriting asset: {e}")
            raise
    
    async def rate_asset(
        self,
        asset_id: str,
        user_id: str,
        rating: float
    ) -> bool:
        """Rate an asset"""
        try:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            if not 1.0 <= rating <= 5.0:
                raise ValueError("Rating must be between 1.0 and 5.0")
            
            asset = self.assets[asset_id]
            
            # Check access permission
            if not await self._check_access_permission(asset, user_id):
                raise ValueError("User not authorized to access this asset")
            
            asset.ratings.append(rating)
            logger.info(f"Asset {asset_id} rated {rating} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error rating asset: {e}")
            raise
    
    async def get_asset_statistics(
        self,
        asset_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive asset statistics"""
        try:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            asset = self.assets[asset_id]
            
            # Calculate statistics
            avg_rating = sum(asset.ratings) / len(asset.ratings) if asset.ratings else 0
            usage_last_30_days = len([
                u for u in self.usage_history 
                if u.asset_id == asset_id and 
                (datetime.now().timestamp() - (u.used_at or 0)) <= 30 * 24 * 3600
            ])
            
            return {
                'asset_id': asset_id,
                'downloads': asset.downloads,
                'usage_count': asset.usage_count,
                'favorites': asset.favorites,
                'average_rating': avg_rating,
                'total_ratings': len(asset.ratings),
                'usage_last_30_days': usage_last_30_days,
                'versions_count': len(asset.versions),
                'file_size_total': sum(v.size for v in asset.versions),
                'created_at': asset.created_at,
                'updated_at': asset.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting asset statistics: {e}")
            raise
    
    async def _check_access_permission(
        self,
        asset: SharedAsset,
        user_id: str
    ) -> bool:
        """Check if user has access permission to asset"""
        try:
            if asset.access_level == AccessLevel.PUBLIC:
                return True
            
            if asset.owner_id == user_id:
                return True
            
            if asset.access_level == AccessLevel.PRIVATE:
                return False
            
            if asset.access_level == AccessLevel.RESTRICTED:
                return user_id in asset.authorized_users
            
            # For team-level access, check team membership
            if asset.access_level in [AccessLevel.TEAM_READ, AccessLevel.TEAM_EDIT]:
                # TODO: Implement team membership check
                return True  # Simplified for now
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking access permission: {e}")
            return False
    
    async def _check_edit_permission(
        self,
        asset: SharedAsset,
        user_id: str
    ) -> bool:
        """Check if user has edit permission to asset"""
        try:
            if asset.owner_id == user_id:
                return True
            
            if asset.access_level == AccessLevel.TEAM_EDIT:
                # TODO: Implement team membership check
                return True  # Simplified for now
            
            if asset.access_level == AccessLevel.RESTRICTED:
                return user_id in asset.authorized_users
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking edit permission: {e}")
            return False
    
    async def _find_asset_by_hash(
        self,
        file_hash: str
    ) -> Optional[SharedAsset]:
        """Find existing asset by file hash"""
        try:
            for asset in self.assets.values():
                for version in asset.versions:
                    if version.file_hash == file_hash:
                        return asset
            return None
            
        except Exception as e:
            logger.error(f"Error finding asset by hash: {e}")
            return None
    
    async def _extract_file_metadata(
        self,
        file_data: bytes,
        filename: str,
        asset_type: AssetType
    ) -> Dict[str, Any]:
        """Extract metadata from file"""
        try:
            metadata = {
                'filename': filename,
                'size': len(file_data),
                'format': Path(filename).suffix.lower()
            }
            
            # TODO: Implement specific metadata extraction for different file types
            # This would use libraries like PIL for images, OpenCV for videos, etc.
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting file metadata: {e}")
            return {}
    
    async def _track_usage(
        self,
        asset_id: str,
        user_id: str,
        project_id: Optional[str] = None,
        context: str = "download"
    ):
        """Track asset usage"""
        try:
            usage = AssetUsage(
                asset_id=asset_id,
                user_id=user_id,
                project_id=project_id,
                usage_context=context
            )
            
            self.usage_history.append(usage)
            
            # Update asset counters
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                if context == "download":
                    asset.downloads += 1
                asset.usage_count += 1
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")


# Export main classes
__all__ = [
    'SharedAssetsManager',
    'SharedAsset',
    'AssetCollection',
    'AssetVersion',
    'AssetMetadata',
    'AssetUsage',
    'AssetType',
    'AssetCategory',
    'AccessLevel',
    'AssetStatus'
]