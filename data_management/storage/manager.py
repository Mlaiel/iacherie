"""
🗄️ Storage Manager - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/storage/manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

Enterprise-grade storage management system for multi-format content
with intelligent tiering, multi-cloud support, and advanced features.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, AsyncGenerator
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
import json
import aiofiles
import aiohttp
from contextlib import asynccontextmanager

from .providers.cloud_provider import CloudStorageProvider
from .providers.local_provider import LocalStorageProvider
from .providers.cdn_provider import CDNStorageProvider
from .providers.cache_provider import CacheStorageProvider
from .engines.lifecycle_engine import LifecycleEngine
from .engines.replication_engine import ReplicationEngine
from .engines.compression_engine import CompressionEngine
from .engines.encryption_engine import EncryptionEngine
from .engines.deduplication_engine import DeduplicationEngine
from .utils.metadata_extractor import MetadataExtractor
from .utils.content_analyzer import ContentAnalyzer
from .utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class StorageTier(Enum):
    """Storage tiers based on access frequency and business requirements"""
    HOT = "hot"          # Frequently accessed (< 30 days) - Active content
    WARM = "warm"        # Occasional access (30-90 days) - Recent content  
    COLD = "cold"        # Rare access (90-365 days) - Archived content
    ARCHIVE = "archive"  # Long-term storage (> 365 days) - Historical data

class ContentType(Enum):
    """Content types for specialized handling"""
    AUDIO = "audio"           # Music, podcasts, sound effects
    VIDEO = "video"           # Performance videos, tutorials
    IMAGE = "image"           # Album covers, photos, artwork
    TEXT = "text"             # Lyrics, blog posts, descriptions
    FINGERPRINT = "fingerprint"  # AI-generated fingerprints
    EMBEDDING = "embedding"   # ML embeddings and vectors
    MODEL = "model"           # Trained ML models
    DOCUMENT = "document"     # PDFs, contracts, licenses
    METADATA = "metadata"     # Analytics, logs, metrics

@dataclass
class StorageRequest:
    """Request for storage operations"""
    content: Union[bytes, BinaryIO, str]
    filename: str
    content_type: ContentType
    metadata: Dict[str, Any] = field(default_factory=dict)
    tier: Optional[StorageTier] = None
    encryption_required: bool = True
    compression_enabled: bool = True
    replicate_count: int = 2
    cdn_distribution: bool = False
    tags: List[str] = field(default_factory=list)

@dataclass
class StorageResponse:
    """Response from storage operations"""
    success: bool
    storage_id: str
    file_path: str
    file_size: int
    checksum: str
    tier: StorageTier
    providers: List[str]
    cdn_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time: float = 0.0

class StorageManager:
    """
    Enterprise storage manager for IA Influencer Agent platform.
    
    Handles multi-format content with intelligent tiering, replication,
    encryption, compression, and distribution across multiple providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize storage manager with configuration"""
        self.config = config
        self.providers: Dict[str, Any] = {}
        self.engines: Dict[str, Any] = {}
        self.performance_monitor = PerformanceMonitor()
        self.metadata_extractor = MetadataExtractor()
        self.content_analyzer = ContentAnalyzer()
        
        # Initialize providers
        self._initialize_providers()
        
        # Initialize engines
        self._initialize_engines()
        
        # Storage statistics
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'requests_count': 0,
            'error_count': 0,
            'performance_metrics': {}
        }
        
        logger.info("StorageManager initialized successfully")
    
    def _initialize_providers(self) -> None:
        """Initialize storage providers based on configuration"""
        try:
            # Cloud providers
            if self.config.get('cloud_enabled', True):
                self.providers['cloud'] = CloudStorageProvider(
                    self.config.get('cloud_config', {})
                )
            
            # Local storage
            if self.config.get('local_enabled', True):
                self.providers['local'] = LocalStorageProvider(
                    self.config.get('local_config', {})
                )
            
            # CDN provider
            if self.config.get('cdn_enabled', True):
                self.providers['cdn'] = CDNStorageProvider(
                    self.config.get('cdn_config', {})
                )
            
            # Cache provider
            if self.config.get('cache_enabled', True):
                self.providers['cache'] = CacheStorageProvider(
                    self.config.get('cache_config', {})
                )
                
            logger.info(f"Initialized {len(self.providers)} storage providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize providers: {str(e)}")
            raise
    
    def _initialize_engines(self) -> None:
        """Initialize processing engines"""
        try:
            self.engines['lifecycle'] = LifecycleEngine(
                self.config.get('lifecycle_config', {})
            )
            self.engines['replication'] = ReplicationEngine(
                self.config.get('replication_config', {})
            )
            self.engines['compression'] = CompressionEngine(
                self.config.get('compression_config', {})
            )
            self.engines['encryption'] = EncryptionEngine(
                self.config.get('encryption_config', {})
            )
            self.engines['deduplication'] = DeduplicationEngine(
                self.config.get('deduplication_config', {})
            )
            
            logger.info(f"Initialized {len(self.engines)} processing engines")
            
        except Exception as e:
            logger.error(f"Failed to initialize engines: {str(e)}")
            raise
    
    async def store_content(self, request: StorageRequest) -> StorageResponse:
        """
        Store content with intelligent processing and distribution.
        
        Business Logic:
        1. Analyze content and extract metadata
        2. Check for duplicates (deduplication)
        3. Determine optimal storage tier
        4. Apply compression if enabled
        5. Encrypt content if required
        6. Store in primary and replica locations
        7. Distribute to CDN if requested
        8. Update metadata and analytics
        """
        start_time = datetime.now()
        
        try:
            # Validate request
            if not request.content or not request.filename:
                raise ValueError("Content and filename are required")
            
            # Extract and analyze content
            content_data = await self._prepare_content(request.content)
            content_hash = self._calculate_hash(content_data)
            
            # Check for existing content (deduplication)
            existing_file = await self._check_duplicate(content_hash)
            if existing_file:
                logger.info(f"Duplicate content found, returning existing: {existing_file}")
                return existing_file
            
            # Analyze content and extract metadata
            content_metadata = await self._analyze_content(
                content_data, request.filename, request.content_type
            )
            
            # Determine storage tier if not specified
            if not request.tier:
                request.tier = await self._determine_tier(
                    request.content_type, content_metadata
                )
            
            # Process content through engines
            processed_content = await self._process_content(
                content_data, request
            )
            
            # Generate storage ID and paths
            storage_id = self._generate_storage_id(content_hash, request.filename)
            file_paths = self._generate_file_paths(storage_id, request.tier)
            
            # Store in primary and replica locations
            storage_results = await self._store_in_providers(
                processed_content, file_paths, request
            )
            
            # Distribute to CDN if requested
            cdn_urls = []
            if request.cdn_distribution:
                cdn_urls = await self._distribute_to_cdn(
                    processed_content, storage_id, request
                )
            
            # Prepare response metadata
            response_metadata = {
                **content_metadata,
                **request.metadata,
                'original_size': len(content_data),
                'processed_size': len(processed_content),
                'compression_ratio': len(processed_content) / len(content_data),
                'storage_tier': request.tier.value,
                'created_at': datetime.now().isoformat(),
                'content_hash': content_hash,
                'tags': request.tags
            }
            
            # Update statistics
            self._update_statistics(storage_results, response_metadata)
            
            # Create response
            response = StorageResponse(
                success=True,
                storage_id=storage_id,
                file_path=file_paths['primary'],
                file_size=len(processed_content),
                checksum=content_hash,
                tier=request.tier,
                providers=list(storage_results.keys()),
                cdn_urls=cdn_urls,
                metadata=response_metadata,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            logger.info(f"Content stored successfully: {storage_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to store content: {str(e)}")
            self.stats['error_count'] += 1
            
            return StorageResponse(
                success=False,
                storage_id="",
                file_path="",
                file_size=0,
                checksum="",
                tier=StorageTier.HOT,
                providers=[],
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def retrieve_content(
        self, 
        storage_id: str, 
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve content by storage ID with optional metadata"""
        try:
            # Check cache first for fast retrieval
            if 'cache' in self.providers:
                cached_content = await self.providers['cache'].get(storage_id)
                if cached_content:
                    logger.info(f"Content retrieved from cache: {storage_id}")
                    return cached_content
            
            # Retrieve from primary storage
            for provider_name, provider in self.providers.items():
                if provider_name == 'cache':
                    continue
                
                try:
                    content = await provider.get(storage_id)
                    if content:
                        # Cache for future requests
                        if 'cache' in self.providers:
                            await self.providers['cache'].put(storage_id, content)
                        
                        logger.info(f"Content retrieved from {provider_name}: {storage_id}")
                        return content
                        
                except Exception as e:
                    logger.warning(f"Failed to retrieve from {provider_name}: {str(e)}")
                    continue
            
            logger.warning(f"Content not found: {storage_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve content {storage_id}: {str(e)}")
            return None
    
    async def delete_content(self, storage_id: str) -> bool:
        """Delete content from all storage locations"""
        try:
            success_count = 0
            total_providers = len(self.providers)
            
            # Delete from all providers
            for provider_name, provider in self.providers.items():
                try:
                    if await provider.delete(storage_id):
                        success_count += 1
                        logger.info(f"Deleted from {provider_name}: {storage_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete from {provider_name}: {str(e)}")
            
            # Consider successful if deleted from at least half of providers
            success = success_count >= (total_providers / 2)
            
            if success:
                logger.info(f"Content deleted successfully: {storage_id}")
            else:
                logger.error(f"Failed to delete content: {storage_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete content {storage_id}: {str(e)}")
            return False
    
    async def list_content(
        self, 
        content_type: Optional[ContentType] = None,
        tier: Optional[StorageTier] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List stored content with filtering options"""
        try:
            # Use primary provider for listing
            primary_provider = self.providers.get('cloud') or self.providers.get('local')
            if not primary_provider:
                logger.error("No primary provider available for listing")
                return []
            
            content_list = await primary_provider.list(
                content_type=content_type.value if content_type else None,
                tier=tier.value if tier else None,
                tags=tags,
                limit=limit,
                offset=offset
            )
            
            logger.info(f"Listed {len(content_list)} content items")
            return content_list
            
        except Exception as e:
            logger.error(f"Failed to list content: {str(e)}")
            return []
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        try:
            # Collect statistics from all providers
            provider_stats = {}
            for provider_name, provider in self.providers.items():
                try:
                    stats = await provider.get_statistics()
                    provider_stats[provider_name] = stats
                except Exception as e:
                    logger.warning(f"Failed to get stats from {provider_name}: {str(e)}")
            
            # Combine with internal statistics
            combined_stats = {
                'internal_stats': self.stats,
                'provider_stats': provider_stats,
                'performance_metrics': await self.performance_monitor.get_metrics(),
                'timestamp': datetime.now().isoformat()
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {str(e)}")
            return {}
    
    async def optimize_storage(self) -> Dict[str, Any]:
        """Run storage optimization tasks"""
        try:
            optimization_results = {}
            
            # Run lifecycle management
            if 'lifecycle' in self.engines:
                lifecycle_result = await self.engines['lifecycle'].optimize()
                optimization_results['lifecycle'] = lifecycle_result
            
            # Run deduplication
            if 'deduplication' in self.engines:
                dedup_result = await self.engines['deduplication'].optimize()
                optimization_results['deduplication'] = dedup_result
            
            # Cleanup old cache entries
            if 'cache' in self.providers:
                cache_result = await self.providers['cache'].cleanup()
                optimization_results['cache_cleanup'] = cache_result
            
            logger.info("Storage optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _prepare_content(self, content: Union[bytes, BinaryIO, str]) -> bytes:
        """Prepare content for processing"""
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode('utf-8')
        elif hasattr(content, 'read'):
            if hasattr(content, 'read'):
                return await content.read() if asyncio.iscoroutinefunction(content.read) else content.read()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    async def _check_duplicate(self, content_hash: str) -> Optional[StorageResponse]:
        """Check if content with same hash already exists"""
        try:
            if 'deduplication' in self.engines:
                return await self.engines['deduplication'].check_duplicate(content_hash)
            return None
        except Exception as e:
            logger.warning(f"Duplicate check failed: {str(e)}")
            return None
    
    async def _analyze_content(
        self, 
        content: bytes, 
        filename: str, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze content and extract metadata"""
        try:
            # Basic metadata
            metadata = {
                'filename': filename,
                'content_type': content_type.value,
                'file_size': len(content),
                'mime_type': mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            }
            
            # Extract detailed metadata based on content type
            if content_type == ContentType.AUDIO:
                audio_metadata = await self.metadata_extractor.extract_audio_metadata(content)
                metadata.update(audio_metadata)
            elif content_type == ContentType.VIDEO:
                video_metadata = await self.metadata_extractor.extract_video_metadata(content)
                metadata.update(video_metadata)
            elif content_type == ContentType.IMAGE:
                image_metadata = await self.metadata_extractor.extract_image_metadata(content)
                metadata.update(image_metadata)
            
            # Content analysis for ML features
            analysis_features = await self.content_analyzer.analyze(content, content_type)
            metadata['analysis'] = analysis_features
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Content analysis failed: {str(e)}")
            return {'filename': filename, 'content_type': content_type.value}
    
    async def _determine_tier(
        self, 
        content_type: ContentType, 
        metadata: Dict[str, Any]
    ) -> StorageTier:
        """Determine optimal storage tier based on content and business rules"""
        try:
            # Business logic for tier assignment
            
            # High-priority content types go to HOT tier
            if content_type in [ContentType.FINGERPRINT, ContentType.EMBEDDING]:
                return StorageTier.HOT
            
            # Active content based on metadata
            if metadata.get('is_active', False) or metadata.get('recent_views', 0) > 1000:
                return StorageTier.HOT
            
            # Recent content goes to WARM tier
            created_at = metadata.get('created_at')
            if created_at:
                created_date = datetime.fromisoformat(created_at)
                if (datetime.now() - created_date).days < 30:
                    return StorageTier.WARM
            
            # Large files or archives go to COLD tier
            if metadata.get('file_size', 0) > 100 * 1024 * 1024:  # 100MB
                return StorageTier.COLD
            
            # Default to WARM tier
            return StorageTier.WARM
            
        except Exception as e:
            logger.warning(f"Tier determination failed: {str(e)}")
            return StorageTier.HOT  # Safe default
    
    async def _process_content(
        self, 
        content: bytes, 
        request: StorageRequest
    ) -> bytes:
        """Process content through configured engines"""
        processed_content = content
        
        try:
            # Apply compression if enabled
            if request.compression_enabled and 'compression' in self.engines:
                processed_content = await self.engines['compression'].compress(
                    processed_content, request.content_type
                )
            
            # Apply encryption if required
            if request.encryption_required and 'encryption' in self.engines:
                processed_content = await self.engines['encryption'].encrypt(
                    processed_content
                )
            
            return processed_content
            
        except Exception as e:
            logger.error(f"Content processing failed: {str(e)}")
            return content  # Return original content on processing failure
    
    def _generate_storage_id(self, content_hash: str, filename: str) -> str:
        """Generate unique storage identifier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_part = Path(filename).stem[:20]  # Limit filename part
        return f"{timestamp}_{file_part}_{content_hash[:12]}"
    
    def _generate_file_paths(
        self, 
        storage_id: str, 
        tier: StorageTier
    ) -> Dict[str, str]:
        """Generate file paths for different storage locations"""
        year = datetime.now().year
        month = datetime.now().month
        
        base_path = f"{tier.value}/{year:04d}/{month:02d}"
        
        return {
            'primary': f"{base_path}/{storage_id}",
            'replica': f"{base_path}/replicas/{storage_id}",
            'cache': f"cache/{storage_id}",
            'cdn': f"cdn/{base_path}/{storage_id}"
        }
    
    async def _store_in_providers(
        self, 
        content: bytes, 
        file_paths: Dict[str, str], 
        request: StorageRequest
    ) -> Dict[str, bool]:
        """Store content in configured providers"""
        results = {}
        
        # Store in primary providers
        primary_providers = ['cloud', 'local']
        for provider_name in primary_providers:
            if provider_name in self.providers:
                try:
                    success = await self.providers[provider_name].put(
                        file_paths['primary'], content, request.metadata
                    )
                    results[provider_name] = success
                    if success:
                        logger.info(f"Stored in {provider_name}: {file_paths['primary']}")
                except Exception as e:
                    logger.error(f"Failed to store in {provider_name}: {str(e)}")
                    results[provider_name] = False
        
        # Create replicas if requested
        if request.replicate_count > 1:
            for i in range(request.replicate_count - 1):
                replica_path = f"{file_paths['replica']}_{i+1}"
                for provider_name in primary_providers:
                    if provider_name in self.providers and results.get(provider_name):
                        try:
                            await self.providers[provider_name].put(
                                replica_path, content, request.metadata
                            )
                            logger.info(f"Replica {i+1} stored in {provider_name}")
                        except Exception as e:
                            logger.warning(f"Failed to create replica in {provider_name}: {str(e)}")
        
        return results
    
    async def _distribute_to_cdn(
        self, 
        content: bytes, 
        storage_id: str, 
        request: StorageRequest
    ) -> List[str]:
        """Distribute content to CDN for global access"""
        cdn_urls = []
        
        if 'cdn' in self.providers:
            try:
                urls = await self.providers['cdn'].distribute(
                    storage_id, content, request.metadata
                )
                cdn_urls.extend(urls)
                logger.info(f"Content distributed to CDN: {len(urls)} URLs")
            except Exception as e:
                logger.error(f"CDN distribution failed: {str(e)}")
        
        return cdn_urls
    
    def _update_statistics(
        self, 
        storage_results: Dict[str, bool], 
        metadata: Dict[str, Any]
    ) -> None:
        """Update internal statistics"""
        self.stats['total_files'] += 1
        self.stats['total_size'] += metadata.get('processed_size', 0)
        self.stats['requests_count'] += 1
        
        # Update performance metrics
        self.performance_monitor.record_operation(
            operation='store',
            success=any(storage_results.values()),
            processing_time=metadata.get('processing_time', 0),
            file_size=metadata.get('processed_size', 0)
        )

# Export main class
__all__ = ['StorageManager', 'StorageRequest', 'StorageResponse', 'StorageTier', 'ContentType']
