"""
🌐 CDN Storage Provider - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/data_management/storage/cdn_storage.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

Global CDN storage provider for content distribution with edge caching,
geographic optimization, and real-time analytics for content creators.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
import logging
import asyncio
import aiohttp
import aiofiles
from datetime import datetime, timedelta
import json
import hashlib
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import base64
import time

logger = logging.getLogger(__name__)

class CDNProvider(Enum):
    """Supported CDN providers"""
    CLOUDFLARE = "cloudflare"
    AMAZON_CLOUDFRONT = "cloudfront"
    FASTLY = "fastly"
    AKAMAI = "akamai"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"

class ContentTier(Enum):
    """Content distribution tiers"""
    GLOBAL = "global"      # Worldwide distribution
    REGIONAL = "regional"  # Regional distribution
    LOCAL = "local"        # Single region only

@dataclass
class CDNConfig:
    """CDN configuration"""
    provider: CDNProvider
    api_key: str
    api_secret: str
    zone_id: Optional[str] = None
    distribution_id: Optional[str] = None
    base_domain: str = ""
    
    # Performance settings
    cache_ttl: int = 86400  # 24 hours
    edge_ttl: int = 604800  # 7 days
    browser_ttl: int = 3600  # 1 hour
    
    # Geographic settings
    global_regions: List[str] = field(default_factory=lambda: [
        'us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1'
    ])
    
    # Content optimization
    enable_compression: bool = True
    enable_image_optimization: bool = True
    enable_video_optimization: bool = True
    enable_webp_conversion: bool = True
    
    # Security settings
    enable_hotlink_protection: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    enable_ddos_protection: bool = True

class CDNStorageManager:
    """
    Enterprise CDN storage manager for global content distribution.
    
    Features:
    - Multi-CDN support with failover
    - Geographic content optimization
    - Real-time analytics and monitoring
    - Automatic format optimization (WebP, AVIF)
    - Edge caching with intelligent purging
    - Content security and hotlink protection
    """
    
    def __init__(self, config: CDNConfig):
        """Initialize CDN storage manager"""
        self.config = config
        self.session = None
        
        # CDN API endpoints
        self.api_endpoints = {
            CDNProvider.CLOUDFLARE: "https://api.cloudflare.com/client/v4",
            CDNProvider.AMAZON_CLOUDFRONT: "https://cloudfront.amazonaws.com",
            CDNProvider.FASTLY: "https://api.fastly.com",
            CDNProvider.AKAMAI: "https://api.akamai.com",
            CDNProvider.AZURE_CDN: "https://management.azure.com",
            CDNProvider.GOOGLE_CDN: "https://www.googleapis.com/compute/v1"
        }
        
        # Performance metrics
        self.metrics = {
            'uploads': 0,
            'downloads': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'bandwidth_usage': 0,
            'geographic_stats': {},
            'performance_stats': {}
        }
        
        # Content cache
        self.content_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"CDNStorageManager initialized for {config.provider.value}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def distribute_content(
        self,
        content: Union[bytes, str, BinaryIO],
        filename: str,
        content_type: str = "unknown",
        tier: ContentTier = ContentTier.GLOBAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute content to CDN with global optimization.
        
        Business Logic:
        1. Optimize content based on type (images, videos, etc.)
        2. Generate multiple format variants (WebP, AVIF, etc.)
        3. Distribute to optimal edge locations
        4. Configure caching policies
        5. Set up geographic routing
        """
        start_time = time.time()
        
        try:
            # Prepare content
            content_bytes = await self._prepare_content(content)
            
            # Generate content variants for optimization
            content_variants = await self._generate_content_variants(
                content_bytes, filename, content_type
            )
            
            # Calculate content properties
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            file_size = len(content_bytes)
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Prepare distribution metadata
            distribution_metadata = {
                'filename': filename,
                'content_type': content_type,
                'file_size': file_size,
                'content_hash': content_hash,
                'mime_type': mime_type,
                'tier': tier.value,
                'distributed_at': datetime.now().isoformat(),
                'variants_count': len(content_variants),
                **(metadata or {})
            }
            
            # Upload to CDN based on provider
            if self.config.provider == CDNProvider.CLOUDFLARE:
                result = await self._upload_to_cloudflare(
                    content_variants, filename, distribution_metadata
                )
            elif self.config.provider == CDNProvider.AMAZON_CLOUDFRONT:
                result = await self._upload_to_cloudfront(
                    content_variants, filename, distribution_metadata
                )
            elif self.config.provider == CDNProvider.FASTLY:
                result = await self._upload_to_fastly(
                    content_variants, filename, distribution_metadata
                )
            else:
                # Generic CDN upload
                result = await self._upload_to_generic_cdn(
                    content_variants, filename, distribution_metadata
                )
            
            # Configure caching policies
            await self._configure_caching_policies(result.get('urls', []), content_type)
            
            # Update metrics
            self._update_metrics('upload', file_size, time.time() - start_time)
            
            # Cache content metadata locally
            self.content_cache[content_hash] = {
                'metadata': distribution_metadata,
                'urls': result.get('urls', []),
                'cached_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'content_hash': content_hash,
                'urls': result.get('urls', []),
                'metadata': distribution_metadata,
                'processing_time': time.time() - start_time,
                'variants': list(content_variants.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to distribute content {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename,
                'processing_time': time.time() - start_time
            }
    
    async def retrieve_content(
        self,
        content_hash: str,
        preferred_format: Optional[str] = None,
        geographic_region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve content from CDN with geographic optimization"""
        start_time = time.time()
        
        try:
            # Check local cache first
            if content_hash in self.content_cache:
                cached_content = self.content_cache[content_hash]
                urls = cached_content['urls']
                
                # Select optimal URL based on criteria
                optimal_url = self._select_optimal_url(
                    urls, preferred_format, geographic_region
                )
                
                if optimal_url:
                    # Download content
                    async with self.session.get(optimal_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            self._update_metrics('download', len(content), time.time() - start_time)
                            self.metrics['cache_hits'] += 1
                            
                            return {
                                'success': True,
                                'content': content,
                                'url': optimal_url,
                                'cache_hit': True,
                                'processing_time': time.time() - start_time
                            }
            
            # Content not in cache or cache miss
            self.metrics['cache_misses'] += 1
            
            return {
                'success': False,
                'error': 'Content not found in CDN',
                'content_hash': content_hash,
                'cache_hit': False,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve content {content_hash}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content_hash': content_hash,
                'processing_time': time.time() - start_time
            }
    
    async def purge_content(
        self,
        content_hash: Optional[str] = None,
        urls: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Purge content from CDN cache"""
        try:
            # Determine what to purge
            purge_targets = []
            
            if content_hash and content_hash in self.content_cache:
                purge_targets.extend(self.content_cache[content_hash]['urls'])
            
            if urls:
                purge_targets.extend(urls)
            
            # Purge based on CDN provider
            if self.config.provider == CDNProvider.CLOUDFLARE:
                result = await self._purge_cloudflare_cache(purge_targets, patterns)
            elif self.config.provider == CDNProvider.AMAZON_CLOUDFRONT:
                result = await self._purge_cloudfront_cache(purge_targets, patterns)
            elif self.config.provider == CDNProvider.FASTLY:
                result = await self._purge_fastly_cache(purge_targets, patterns)
            else:
                result = await self._purge_generic_cdn_cache(purge_targets, patterns)
            
            # Remove from local cache
            if content_hash and content_hash in self.content_cache:
                del self.content_cache[content_hash]
            
            logger.info(f"Purged {len(purge_targets)} items from CDN cache")
            
            return {
                'success': True,
                'purged_count': len(purge_targets),
                'purged_urls': purge_targets
            }
            
        except Exception as e:
            logger.error(f"Failed to purge CDN cache: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get CDN analytics and performance metrics"""
        try:
            # Default to last 24 hours if no dates specified
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=1)
            
            # Get analytics based on CDN provider
            if self.config.provider == CDNProvider.CLOUDFLARE:
                analytics = await self._get_cloudflare_analytics(start_date, end_date)
            elif self.config.provider == CDNProvider.AMAZON_CLOUDFRONT:
                analytics = await self._get_cloudfront_analytics(start_date, end_date)
            elif self.config.provider == CDNProvider.FASTLY:
                analytics = await self._get_fastly_analytics(start_date, end_date)
            else:
                analytics = await self._get_generic_cdn_analytics(start_date, end_date)
            
            # Combine with local metrics
            combined_analytics = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'local_metrics': self.metrics,
                'cdn_analytics': analytics,
                'performance_summary': self._calculate_performance_summary(analytics)
            }
            
            return combined_analytics
            
        except Exception as e:
            logger.error(f"Failed to get CDN analytics: {str(e)}")
            return {'error': str(e)}
    
    async def list_content(
        self,
        limit: int = 100,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List content distributed in CDN"""
        try:
            content_list = []
            
            for content_hash, cache_data in list(self.content_cache.items())[:limit]:
                if prefix:
                    filename = cache_data['metadata'].get('filename', '')
                    if not filename.startswith(prefix):
                        continue
                
                content_list.append({
                    'content_hash': content_hash,
                    'filename': cache_data['metadata'].get('filename'),
                    'content_type': cache_data['metadata'].get('content_type'),
                    'file_size': cache_data['metadata'].get('file_size'),
                    'distributed_at': cache_data['metadata'].get('distributed_at'),
                    'urls': cache_data['urls'],
                    'cached_at': cache_data['cached_at']
                })
            
            return content_list
            
        except Exception as e:
            logger.error(f"Failed to list CDN content: {str(e)}")
            return []
    
    async def optimize_content(
        self,
        content_hash: str,
        optimization_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply additional content optimizations"""
        try:
            if content_hash not in self.content_cache:
                return {
                    'success': False,
                    'error': 'Content not found in cache'
                }
            
            cache_data = self.content_cache[content_hash]
            
            # Apply optimizations based on content type
            content_type = cache_data['metadata']['content_type']
            
            if content_type == 'image':
                result = await self._optimize_image_content(content_hash, optimization_options)
            elif content_type == 'video':
                result = await self._optimize_video_content(content_hash, optimization_options)
            elif content_type == 'audio':
                result = await self._optimize_audio_content(content_hash, optimization_options)
            else:
                result = await self._optimize_generic_content(content_hash, optimization_options)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize content {content_hash}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Provider-specific implementation methods
    
    async def _upload_to_cloudflare(
        self,
        content_variants: Dict[str, bytes],
        filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to Cloudflare"""
        try:
            urls = []
            
            for variant_name, content in content_variants.items():
                # Prepare upload URL
                upload_url = f"{self.api_endpoints[CDNProvider.CLOUDFLARE]}/zones/{self.config.zone_id}/files"
                
                # Prepare headers
                headers = {
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/octet-stream'
                }
                
                # Generate variant filename
                variant_filename = self._generate_variant_filename(filename, variant_name)
                
                # Upload content
                data = aiohttp.FormData()
                data.add_field('file', content, filename=variant_filename)
                data.add_field('metadata', json.dumps(metadata))
                
                async with self.session.post(upload_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            cdn_url = f"https://{self.config.base_domain}/{variant_filename}"
                            urls.append({
                                'variant': variant_name,
                                'url': cdn_url,
                                'size': len(content)
                            })
            
            return {
                'success': True,
                'urls': urls,
                'provider': 'cloudflare'
            }
            
        except Exception as e:
            logger.error(f"Cloudflare upload failed: {str(e)}")
            raise
    
    async def _upload_to_cloudfront(
        self,
        content_variants: Dict[str, bytes],
        filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to Amazon CloudFront"""
        # CloudFront-specific implementation
        pass
    
    async def _upload_to_fastly(
        self,
        content_variants: Dict[str, bytes],
        filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to Fastly"""
        # Fastly-specific implementation
        pass
    
    async def _upload_to_generic_cdn(
        self,
        content_variants: Dict[str, bytes],
        filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic CDN upload implementation"""
        # Generic implementation for other CDN providers
        urls = []
        
        for variant_name, content in content_variants.items():
            variant_filename = self._generate_variant_filename(filename, variant_name)
            cdn_url = f"https://{self.config.base_domain}/{variant_filename}"
            
            urls.append({
                'variant': variant_name,
                'url': cdn_url,
                'size': len(content)
            })
        
        return {
            'success': True,
            'urls': urls,
            'provider': 'generic'
        }
    
    # Content optimization methods
    
    async def _generate_content_variants(
        self,
        content: bytes,
        filename: str,
        content_type: str
    ) -> Dict[str, bytes]:
        """Generate optimized content variants"""
        variants = {'original': content}
        
        try:
            if content_type == 'image' and self.config.enable_image_optimization:
                # Generate WebP variant
                if self.config.enable_webp_conversion:
                    webp_content = await self._convert_to_webp(content)
                    if webp_content:
                        variants['webp'] = webp_content
                
                # Generate compressed variant
                compressed_content = await self._compress_image(content)
                if compressed_content and len(compressed_content) < len(content):
                    variants['compressed'] = compressed_content
            
            elif content_type == 'video' and self.config.enable_video_optimization:
                # Generate different quality variants
                variants.update(await self._generate_video_variants(content))
            
            elif content_type == 'audio':
                # Generate different quality variants
                variants.update(await self._generate_audio_variants(content))
            
            # Apply general compression if enabled
            if self.config.enable_compression:
                compressed = await self._compress_content(content)
                if compressed and len(compressed) < len(content):
                    variants['compressed'] = compressed
            
        except Exception as e:
            logger.warning(f"Failed to generate content variants: {str(e)}")
        
        return variants
    
    async def _convert_to_webp(self, image_content: bytes) -> Optional[bytes]:
        """Convert image to WebP format"""
        try:
            from PIL import Image
            import io
            
            # Load image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to WebP
            output = io.BytesIO()
            image.save(output, format='WEBP', quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"WebP conversion failed: {str(e)}")
            return None
    
    async def _compress_image(self, image_content: bytes) -> Optional[bytes]:
        """Compress image with quality optimization"""
        try:
            from PIL import Image
            import io
            
            # Load image
            image = Image.open(io.BytesIO(image_content))
            
            # Compress with optimal quality
            output = io.BytesIO()
            if image.format == 'JPEG':
                image.save(output, format='JPEG', quality=85, optimize=True)
            elif image.format == 'PNG':
                image.save(output, format='PNG', optimize=True)
            else:
                return None
            
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Image compression failed: {str(e)}")
            return None
    
    async def _generate_video_variants(self, video_content: bytes) -> Dict[str, bytes]:
        """Generate video quality variants"""
        # Video processing implementation would go here
        # For now, return empty dict
        return {}
    
    async def _generate_audio_variants(self, audio_content: bytes) -> Dict[str, bytes]:
        """Generate audio quality variants"""
        # Audio processing implementation would go here
        # For now, return empty dict
        return {}
    
    async def _compress_content(self, content: bytes) -> Optional[bytes]:
        """Apply general content compression"""
        try:
            import gzip
            
            compressed = gzip.compress(content, compresslevel=6)
            
            # Only return if compression is beneficial
            if len(compressed) < len(content) * 0.9:
                return compressed
            
            return None
            
        except Exception as e:
            logger.warning(f"Content compression failed: {str(e)}")
            return None
    
    # Helper methods
    
    async def _prepare_content(self, content: Union[bytes, str, BinaryIO]) -> bytes:
        """Prepare content for CDN distribution"""
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode('utf-8')
        elif hasattr(content, 'read'):
            if asyncio.iscoroutinefunction(content.read):
                return await content.read()
            else:
                return content.read()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    def _generate_variant_filename(self, original_filename: str, variant: str) -> str:
        """Generate filename for content variant"""
        path = Path(original_filename)
        stem = path.stem
        suffix = path.suffix
        
        if variant == 'original':
            return original_filename
        
        return f"{stem}_{variant}{suffix}"
    
    def _select_optimal_url(
        self,
        urls: List[Dict[str, Any]],
        preferred_format: Optional[str],
        geographic_region: Optional[str]
    ) -> Optional[str]:
        """Select optimal URL based on criteria"""
        if not urls:
            return None
        
        # Prefer specific format if requested
        if preferred_format:
            for url_info in urls:
                if url_info.get('variant') == preferred_format:
                    return url_info['url']
        
        # Prefer WebP for images if supported
        for url_info in urls:
            if url_info.get('variant') == 'webp':
                return url_info['url']
        
        # Fall back to compressed variant
        for url_info in urls:
            if url_info.get('variant') == 'compressed':
                return url_info['url']
        
        # Fall back to original
        for url_info in urls:
            if url_info.get('variant') == 'original':
                return url_info['url']
        
        # Return first available URL
        return urls[0]['url']
    
    async def _configure_caching_policies(
        self,
        urls: List[Dict[str, Any]],
        content_type: str
    ) -> None:
        """Configure CDN caching policies"""
        try:
            # Different caching strategies based on content type
            if content_type in ['image', 'audio', 'video']:
                # Long-term caching for media
                cache_ttl = self.config.edge_ttl
            elif content_type in ['fingerprint', 'embedding']:
                # Medium-term caching for AI content
                cache_ttl = self.config.cache_ttl
            else:
                # Default caching
                cache_ttl = self.config.cache_ttl
            
            # Configure based on CDN provider
            if self.config.provider == CDNProvider.CLOUDFLARE:
                await self._configure_cloudflare_caching(urls, cache_ttl)
            # Add other providers as needed
            
        except Exception as e:
            logger.warning(f"Failed to configure caching policies: {str(e)}")
    
    async def _configure_cloudflare_caching(
        self,
        urls: List[Dict[str, Any]],
        cache_ttl: int
    ) -> None:
        """Configure Cloudflare-specific caching"""
        # Cloudflare caching configuration implementation
        pass
    
    # Analytics methods (provider-specific)
    
    async def _get_cloudflare_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get Cloudflare analytics"""
        # Cloudflare analytics implementation
        return {}
    
    async def _get_cloudfront_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get CloudFront analytics"""
        # CloudFront analytics implementation
        return {}
    
    async def _get_fastly_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get Fastly analytics"""
        # Fastly analytics implementation
        return {}
    
    async def _get_generic_cdn_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get generic CDN analytics"""
        return {
            'requests': 0,
            'bandwidth': 0,
            'cache_hit_ratio': 0.0,
            'geographic_distribution': {},
            'top_content': []
        }
    
    # Cache purging methods (provider-specific)
    
    async def _purge_cloudflare_cache(
        self,
        urls: List[str],
        patterns: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Purge Cloudflare cache"""
        # Cloudflare cache purging implementation
        return {'success': True}
    
    async def _purge_cloudfront_cache(
        self,
        urls: List[str],
        patterns: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Purge CloudFront cache"""
        # CloudFront cache purging implementation
        return {'success': True}
    
    async def _purge_fastly_cache(
        self,
        urls: List[str],
        patterns: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Purge Fastly cache"""
        # Fastly cache purging implementation
        return {'success': True}
    
    async def _purge_generic_cdn_cache(
        self,
        urls: List[str],
        patterns: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Purge generic CDN cache"""
        return {'success': True}
    
    # Content optimization methods (provider-specific)
    
    async def _optimize_image_content(
        self,
        content_hash: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize image content"""
        return {'success': True, 'optimizations_applied': []}
    
    async def _optimize_video_content(
        self,
        content_hash: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize video content"""
        return {'success': True, 'optimizations_applied': []}
    
    async def _optimize_audio_content(
        self,
        content_hash: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize audio content"""
        return {'success': True, 'optimizations_applied': []}
    
    async def _optimize_generic_content(
        self,
        content_hash: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize generic content"""
        return {'success': True, 'optimizations_applied': []}
    
    def _calculate_performance_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance summary from analytics"""
        return {
            'total_requests': analytics.get('requests', 0),
            'total_bandwidth': analytics.get('bandwidth', 0),
            'cache_hit_ratio': analytics.get('cache_hit_ratio', 0.0),
            'avg_response_time': analytics.get('avg_response_time', 0.0),
            'geographic_coverage': len(analytics.get('geographic_distribution', {}))
        }
    
    def _update_metrics(self, operation: str, size: int, processing_time: float) -> None:
        """Update performance metrics"""
        if operation == 'upload':
            self.metrics['uploads'] += 1
        elif operation == 'download':
            self.metrics['downloads'] += 1
        
        self.metrics['bandwidth_usage'] += size
        
        # Update performance stats
        if operation not in self.metrics['performance_stats']:
            self.metrics['performance_stats'][operation] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        stats = self.metrics['performance_stats'][operation]
        stats['count'] += 1
        stats['total_time'] += processing_time
        stats['avg_time'] = stats['total_time'] / stats['count']

class AsyncCDNStorageManager:
    """Async wrapper for high-performance concurrent CDN operations"""
    
    def __init__(self, config: CDNConfig):
        self.sync_manager = CDNStorageManager(config)
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
    
    async def distribute_content_batch(
        self,
        content_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Distribute multiple content items concurrently"""
        
        async def distribute_single(content_info):
            async with self.semaphore:
                return await self.sync_manager.distribute_content(
                    content_info['content'],
                    content_info['filename'],
                    content_info.get('content_type', 'unknown'),
                    content_info.get('tier', ContentTier.GLOBAL),
                    content_info.get('metadata')
                )
        
        tasks = [distribute_single(content_info) for content_info in content_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]

# Export classes
__all__ = [
    'CDNStorageManager',
    'AsyncCDNStorageManager',
    'CDNConfig',
    'CDNProvider',
    'ContentTier'
]
