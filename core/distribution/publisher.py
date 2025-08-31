"""Content Publisher - Multi-Platform Publishing Engine
===================================================

Handles the actual publishing of content to various platforms with format adaptation,
metadata optimization, and compliance checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
from pathlib import Path

from ..multimedia.processor import MultimediaProcessor
from ..seo.optimizer import SEOOptimizer
from ..security.content_scanner import ContentSecurityScanner
from ..validation.compliance import ComplianceValidator


class PublishingStatus(Enum):
    """Publishing status enumeration."""    PENDING = "pending"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class ContentFormat(Enum):
    """Content format enumeration."""    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"


@dataclass
class PublishingRequest:
    """Publishing request data structure."""    request_id: UUID = field(default_factory=uuid4)
    content_id: UUID = field(default_factory=uuid4)
    platform: str = ""
    content_format: ContentFormat = ContentFormat.VIDEO
    source_file_path: str = ""
    adapted_file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_metadata: Dict[str, Any] = field(default_factory=dict)
    seo_metadata: Dict[str, Any] = field(default_factory=dict)
    targeting_options: Dict[str, Any] = field(default_factory=dict)
    monetization_settings: Dict[str, Any] = field(default_factory=dict)
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    scheduling_options: Dict[str, Any] = field(default_factory=dict)
    thumbnail_path: Optional[str] = None
    captions_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class PublishingResult:
    """Publishing result data structure."""    request_id: UUID
    platform: str
    success: bool
    status: PublishingStatus
    platform_id: Optional[str] = None
    platform_url: Optional[str] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    compliance_checks: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class ContentPublisher:
    """    Content Publisher Engine
    
    Handles multi-platform content publishing with advanced features including
    format adaptation, SEO optimization, compliance checking, and performance tracking.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content publisher."""        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.multimedia_processor = MultimediaProcessor()
        self.seo_optimizer = SEOOptimizer()
        self.security_scanner = ContentSecurityScanner()
        self.compliance_validator = ComplianceValidator()
        
        # Publishing state
        self.active_publications: Dict[UUID, PublishingRequest] = {}
        self.completed_publications: Dict[UUID, PublishingResult] = {}
        self.platform_connections: Dict[str, Any] = {}
        
        # Platform configurations
        self.platform_configs = {}
        self.platform_adapters = {}
        self.platform_limits = {}
        
        # Performance tracking
        self.metrics = {
            'total_publications': 0,
            'successful_publications': 0,
            'failed_publications': 0,
            'platform_metrics': {},
            'format_metrics': {},
            'average_upload_time': 0.0,
            'average_processing_time': 0.0
        }
        
        # System state
        self.is_initialized = False
        self.max_concurrent_uploads = config.get('max_concurrent_uploads', 5)
        self.upload_timeout = config.get('upload_timeout', 3600)  # 1 hour
        self.temp_dir = Path(config.get('temp_dir', '/tmp/publisher'))
        
    async def initialize(self) -> bool:
        """        Initialize the content publisher.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing Content Publisher")
            
            # Initialize core components
            await self.multimedia_processor.initialize()
            await self.seo_optimizer.initialize()
            await self.security_scanner.initialize()
            await self.compliance_validator.initialize()
            
            # Create temp directory
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Load platform configurations
            await self._load_platform_configurations()
            
            # Initialize platform adapters
            await self._initialize_platform_adapters()
            
            # Test platform connections
            await self._test_platform_connections()
            
            self.is_initialized = True
            
            self.logger.info("Content Publisher initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Publisher: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """        Gracefully shutdown the content publisher.
        
        Returns:
            bool: True if shutdown successful
        """        try:
            self.logger.info("Shutting down Content Publisher")
            
            # Wait for active publications to complete
            if self.active_publications:
                self.logger.info(f"Waiting for {len(self.active_publications)} active publications to complete")
                timeout = 300  # 5 minutes timeout
                start_time = datetime.utcnow()
                
                while self.active_publications and (datetime.utcnow() - start_time).seconds < timeout:
                    await asyncio.sleep(5)
                
                if self.active_publications:
                    self.logger.warning(f"Force stopping {len(self.active_publications)} remaining publications")
            
            # Shutdown platform adapters
            await self._shutdown_platform_adapters()
            
            # Cleanup temp files
            await self._cleanup_temp_files()
            
            # Clear state
            self.active_publications.clear()
            self.platform_connections.clear()
            
            self.is_initialized = False
            
            self.logger.info("Content Publisher shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Content Publisher shutdown: {e}")
            return False
    
    async def publish_content(
        self,
        content_id: UUID,
        platform: str,
        metadata: Dict[str, Any],
        targeting_options: Optional[Dict[str, Any]] = None,
        monetization_settings: Optional[Dict[str, Any]] = None,
        privacy_settings: Optional[Dict[str, Any]] = None,
        scheduling_options: Optional[Dict[str, Any]] = None
    ) -> PublishingResult:
        """        Publish content to a specific platform.
        
        Args:
            content_id: Unique identifier for content
            platform: Target platform name
            metadata: Content metadata
            targeting_options: Platform targeting options
            monetization_settings: Monetization configuration
            privacy_settings: Privacy and visibility settings
            scheduling_options: Scheduling configuration
            
        Returns:
            PublishingResult: Result of publishing operation
        """        if not self.is_initialized:
            raise RuntimeError("Content Publisher not initialized")
        
        # Create publishing request
        request = PublishingRequest(
            content_id=content_id,
            platform=platform,
            metadata=metadata,
            targeting_options=targeting_options or {},
            monetization_settings=monetization_settings or {},
            privacy_settings=privacy_settings or {},
            scheduling_options=scheduling_options or {}
        )
        
        self.logger.info(f"Publishing content {content_id} to {platform} (request {request.request_id})")
        
        try:
            # Pre-publishing validation and preparation
            await self._prepare_content_for_publishing(request)
            
            # Execute publishing process
            result = await self._execute_publishing(request)
            
            # Post-publishing actions
            await self._post_publishing_actions(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Publishing failed for request {request.request_id}: {e}")
            
            # Create error result
            result = PublishingResult(
                request_id=request.request_id,
                platform=platform,
                success=False,
                status=PublishingStatus.FAILED,
                error_message=str(e),
                metadata={'error_type': type(e).__name__}
            )
            
            # Update metrics
            self.metrics['failed_publications'] += 1
            self._update_platform_metrics(platform, False)
            
            return result
    
    async def _prepare_content_for_publishing(self, request: PublishingRequest) -> None:
        """Prepare content for publishing."""        self.logger.debug(f"Preparing content for publishing: {request.request_id}")
        
        # Get content information
        content_info = await self._get_content_information(request.content_id)
        request.content_format = ContentFormat(content_info['format'])
        request.source_file_path = content_info['file_path']
        
        # Validate platform compatibility
        await self._validate_platform_compatibility(request)
        
        # Security scanning
        await self._perform_security_scan(request)
        
        # Compliance validation
        await self._validate_compliance(request)
        
        # Content adaptation
        await self._adapt_content_for_platform(request)
        
        # SEO optimization
        await self._optimize_seo_metadata(request)
        
        # Generate thumbnails if needed
        await self._generate_thumbnails(request)
        
        # Process captions/subtitles
        await self._process_captions(request)
    
    async def _execute_publishing(self, request: PublishingRequest) -> PublishingResult:
        """Execute the publishing process."""        start_time = datetime.utcnow()
        processing_start = asyncio.get_event_loop().time()
        
        # Add to active publications
        self.active_publications[request.request_id] = request
        
        try:
            # Get platform adapter
            adapter = self.platform_adapters.get(request.platform)
            if not adapter:
                raise ValueError(f"No adapter available for platform: {request.platform}")
            
            # Create initial result
            result = PublishingResult(
                request_id=request.request_id,
                platform=request.platform,
                success=False,
                status=PublishingStatus.PROCESSING
            )
            
            # Check if scheduled publication
            schedule_time = request.scheduling_options.get('publish_time')
            if schedule_time and isinstance(schedule_time, str):
                schedule_time = datetime.fromisoformat(schedule_time)
            
            if schedule_time and schedule_time > datetime.utcnow():
                result.status = PublishingStatus.SCHEDULED
                result.metadata['scheduled_for'] = schedule_time.isoformat()
                # In a real implementation, this would schedule the publication
                self.logger.info(f"Content scheduled for publication at {schedule_time}")
                return result
            
            # Update status to uploading
            result.status = PublishingStatus.UPLOADING
            
            # Execute platform-specific publishing
            publishing_data = await self._publish_to_platform(adapter, request)
            
            # Process publishing response
            if publishing_data.get('success', False):
                result.success = True
                result.status = PublishingStatus.PUBLISHED
                result.platform_id = publishing_data.get('platform_id')
                result.platform_url = publishing_data.get('platform_url')
                result.published_at = datetime.utcnow()
                result.analytics_data = publishing_data.get('analytics_data', {})
                
                self.logger.info(f"Content published successfully to {request.platform}: {result.platform_url}")
                
                # Update metrics
                self.metrics['successful_publications'] += 1
                self._update_platform_metrics(request.platform, True)
                
            else:
                result.success = False
                result.status = PublishingStatus.FAILED
                result.error_message = publishing_data.get('error_message', 'Unknown publishing error')
                result.warnings = publishing_data.get('warnings', [])
                
                self.logger.error(f"Content publishing failed: {result.error_message}")
                
                # Update metrics
                self.metrics['failed_publications'] += 1
                self._update_platform_metrics(request.platform, False)
            
            # Calculate performance metrics
            processing_time = asyncio.get_event_loop().time() - processing_start
            result.performance_metrics = {
                'processing_time': processing_time,
                'file_size': await self._get_file_size(request.adapted_file_path or request.source_file_path),
                'upload_speed': 0.0  # Would be calculated from actual upload
            }
            
            # Update average processing time
            total_publications = self.metrics['successful_publications'] + self.metrics['failed_publications']
            self.metrics['average_processing_time'] = (
                (self.metrics['average_processing_time'] * (total_publications - 1) + processing_time) 
                / total_publications
            )
            
            # Store completed publication
            self.completed_publications[request.request_id] = result
            
            # Update total metrics
            self.metrics['total_publications'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Publishing execution failed: {e}")
            
            result = PublishingResult(
                request_id=request.request_id,
                platform=request.platform,
                success=False,
                status=PublishingStatus.FAILED,
                error_message=str(e),
                metadata={'error_type': type(e).__name__}
            )
            
            self.metrics['failed_publications'] += 1
            self.metrics['total_publications'] += 1
            self._update_platform_metrics(request.platform, False)
            
            return result
            
        finally:
            # Remove from active publications
            self.active_publications.pop(request.request_id, None)
    
    async def _publish_to_platform(self, adapter: Any, request: PublishingRequest) -> Dict[str, Any]:
        """Publish content using platform adapter."""        # Prepare publication data
        publication_data = {
            'content_id': request.content_id,
            'file_path': request.adapted_file_path or request.source_file_path,
            'metadata': {
                **request.metadata,
                **request.platform_metadata,
                **request.seo_metadata
            },
            'targeting': request.targeting_options,
            'monetization': request.monetization_settings,
            'privacy': request.privacy_settings,
            'thumbnail_path': request.thumbnail_path,
            'captions_path': request.captions_path,
            'compliance_data': request.metadata.get('compliance_checks', {})
        }
        
        # Execute platform-specific publishing
        return await adapter.publish_content(publication_data)
    
    async def _get_content_information(self, content_id: UUID) -> Dict[str, Any]:
        """Get content information from content management system."""        # This would interface with the content management system
        # For now, return mock data
        return {
            'format': 'video',
            'file_path': f'/content/{content_id}.mp4',
            'duration': 120,
            'file_size': 50 * 1024 * 1024,
            'resolution': '1920x1080',
            'codec': 'h264'
        }
    
    async def _validate_platform_compatibility(self, request: PublishingRequest) -> None:
        """Validate content compatibility with platform."""        platform_config = self.platform_configs.get(request.platform)
        if not platform_config:
            raise ValueError(f"Unknown platform: {request.platform}")
        
        # Check format compatibility
        supported_formats = platform_config.get('supported_formats', [])
        if request.content_format.value not in supported_formats:
            raise ValueError(f"Format {request.content_format.value} not supported by {request.platform}")
        
        # Check file size limits
        file_size = await self._get_file_size(request.source_file_path)
        max_size = platform_config.get('max_file_size', 0)
        if max_size > 0 and file_size > max_size:
            raise ValueError(f"File size {file_size} exceeds platform limit {max_size}")
        
        # Check required metadata fields
        required_fields = platform_config.get('required_fields', [])
        missing_fields = [field for field in required_fields if field not in request.metadata]
        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {missing_fields}")
    
    async def _perform_security_scan(self, request: PublishingRequest) -> None:
        """Perform security scan on content."""        scan_result = await self.security_scanner.scan_content(request.source_file_path)
        
        if not scan_result['safe']:
            threats = scan_result.get('threats', [])
            raise SecurityError(f"Content security scan failed: {threats}")
        
        request.metadata['security_scan'] = scan_result
    
    async def _validate_compliance(self, request: PublishingRequest) -> None:
        """Validate content compliance."""        compliance_result = await self.compliance_validator.validate_content(
            content_path=request.source_file_path,
            platform=request.platform,
            metadata=request.metadata
        )
        
        if not compliance_result['compliant']:
            violations = compliance_result.get('violations', [])
            raise ComplianceError(f"Content compliance validation failed: {violations}")
        
        request.metadata['compliance_checks'] = compliance_result
    
    async def _adapt_content_for_platform(self, request: PublishingRequest) -> None:
        """Adapt content for specific platform requirements."""        platform_config = self.platform_configs.get(request.platform, {})
        adaptation_rules = platform_config.get('adaptation_rules', {})
        
        if not adaptation_rules:
            return  # No adaptation needed
        
        # Generate adapted file path
        file_extension = Path(request.source_file_path).suffix
        adapted_filename = f"{request.request_id}_{request.platform}{file_extension}"
        request.adapted_file_path = str(self.temp_dir / adapted_filename)
        
        # Perform content adaptation
        adaptation_result = await self.multimedia_processor.adapt_content(
            source_path=request.source_file_path,
            output_path=request.adapted_file_path,
            adaptation_rules=adaptation_rules,
            content_format=request.content_format
        )
        
        if not adaptation_result['success']:
            raise ProcessingError(f"Content adaptation failed: {adaptation_result.get('error')}")
        
        request.metadata['adaptation'] = adaptation_result
    
    async def _optimize_seo_metadata(self, request: PublishingRequest) -> None:
        """Optimize metadata for SEO."""        seo_result = await self.seo_optimizer.optimize_metadata(
            content_metadata=request.metadata,
            platform=request.platform,
            content_format=request.content_format
        )
        
        request.seo_metadata = seo_result
        request.platform_metadata.update(seo_result.get('platform_specific', {}))
    
    async def _generate_thumbnails(self, request: PublishingRequest) -> None:
        """Generate thumbnails for video content."""        if request.content_format != ContentFormat.VIDEO:
            return
        
        platform_config = self.platform_configs.get(request.platform, {})
        if not platform_config.get('requires_thumbnail', False):
            return
        
        # Generate thumbnail
        thumbnail_filename = f"{request.request_id}_{request.platform}_thumb.jpg"
        thumbnail_path = str(self.temp_dir / thumbnail_filename)
        
        thumbnail_result = await self.multimedia_processor.generate_thumbnail(
            video_path=request.adapted_file_path or request.source_file_path,
            output_path=thumbnail_path,
            timestamp=request.metadata.get('thumbnail_timestamp', 5),  # 5 seconds default
            resolution=platform_config.get('thumbnail_resolution', '1280x720')
        )
        
        if thumbnail_result['success']:
            request.thumbnail_path = thumbnail_path
            request.metadata['thumbnail'] = thumbnail_result
    
    async def _process_captions(self, request: PublishingRequest) -> None:
        """Process captions/subtitles for content."""        if request.content_format not in [ContentFormat.VIDEO, ContentFormat.AUDIO]:
            return
        
        platform_config = self.platform_configs.get(request.platform, {})
        if not platform_config.get('supports_captions', False):
            return
        
        # Check if captions are provided or need to be generated
        captions_data = request.metadata.get('captions')
        if not captions_data:
            # Auto-generate captions if enabled
            if platform_config.get('auto_generate_captions', False):
                captions_result = await self.multimedia_processor.generate_captions(
                    media_path=request.adapted_file_path or request.source_file_path,
                    language=request.metadata.get('language', 'en')
                )
                
                if captions_result['success']:
                    captions_filename = f"{request.request_id}_{request.platform}_captions.srt"
                    request.captions_path = str(self.temp_dir / captions_filename)
                    
                    # Save captions to file
                    with open(request.captions_path, 'w', encoding='utf-8') as f:
                        f.write(captions_result['captions'])
                    
                    request.metadata['captions'] = captions_result
    
    async def _post_publishing_actions(self, request: PublishingRequest, result: PublishingResult) -> None:
        """Perform post-publishing actions."""        try:
            # Cleanup temporary files
            await self._cleanup_request_files(request)
            
            # Update analytics
            await self._update_analytics(request, result)
            
            # Send notifications if configured
            await self._send_publication_notifications(request, result)
            
            # Update content metadata with publication info
            await self._update_content_metadata(request, result)
            
        except Exception as e:
            self.logger.error(f"Error in post-publishing actions: {e}")
    
    async def _cleanup_request_files(self, request: PublishingRequest) -> None:
        """Clean up temporary files for request."""        files_to_cleanup = [
            request.adapted_file_path,
            request.thumbnail_path,
            request.captions_path
        ]
        
        for file_path in files_to_cleanup:
            if file_path and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                    self.logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup file {file_path}: {e}")
    
    async def _update_analytics(self, request: PublishingRequest, result: PublishingResult) -> None:
        """Update analytics with publication data."""        # This would update analytics database
        analytics_data = {
            'content_id': request.content_id,
            'platform': request.platform,
            'success': result.success,
            'published_at': result.published_at,
            'performance_metrics': result.performance_metrics,
            'metadata': result.metadata
        }
        
        # Store analytics data (mock implementation)
        self.logger.debug(f"Updating analytics: {analytics_data}")
    
    async def _send_publication_notifications(self, request: PublishingRequest, result: PublishingResult) -> None:
        """Send publication notifications."""        # This would send notifications to users
        notification_data = {
            'type': 'publication_complete' if result.success else 'publication_failed',
            'content_id': request.content_id,
            'platform': request.platform,
            'result': result
        }
        
        self.logger.debug(f"Sending notification: {notification_data}")
    
    async def _update_content_metadata(self, request: PublishingRequest, result: PublishingResult) -> None:
        """Update content metadata with publication information."""        # This would update the content management system
        update_data = {
            'content_id': request.content_id,
            'platform_publications': {
                request.platform: {
                    'published': result.success,
                    'platform_id': result.platform_id,
                    'platform_url': result.platform_url,
                    'published_at': result.published_at.isoformat() if result.published_at else None
                }
            }
        }
        
        self.logger.debug(f"Updating content metadata: {update_data}")
    
    async def _load_platform_configurations(self) -> None:
        """Load platform configurations."""        # This would typically load from database or configuration files
        self.platform_configs = {
            'youtube': {
                'name': 'YouTube',
                'supported_formats': ['video', 'audio'],
                'max_file_size': 128 * 1024 * 1024 * 1024,  # 128GB
                'required_fields': ['title', 'description'],
                'requires_thumbnail': True,
                'supports_captions': True,
                'auto_generate_captions': True,
                'thumbnail_resolution': '1280x720',
                'adaptation_rules': {
                    'video': {
                        'max_resolution': '1920x1080',
                        'codec': 'h264',
                        'bitrate': '5000k'
                    }
                }
            },
            'instagram': {
                'name': 'Instagram',
                'supported_formats': ['image', 'video'],
                'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
                'required_fields': ['caption'],
                'requires_thumbnail': True,
                'supports_captions': False,
                'thumbnail_resolution': '1080x1080',
                'adaptation_rules': {
                    'video': {
                        'max_resolution': '1080x1080',
                        'duration_limit': 60,
                        'codec': 'h264'
                    }
                }
            },
            'tiktok': {
                'name': 'TikTok',
                'supported_formats': ['video'],
                'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
                'required_fields': ['title'],
                'requires_thumbnail': True,
                'supports_captions': True,
                'thumbnail_resolution': '1080x1920',
                'adaptation_rules': {
                    'video': {
                        'max_resolution': '1080x1920',
                        'duration_limit': 300,
                        'codec': 'h264'
                    }
                }
            },
            'spotify': {
                'name': 'Spotify',
                'supported_formats': ['audio'],
                'max_file_size': 200 * 1024 * 1024,  # 200MB
                'required_fields': ['title', 'artist', 'album'],
                'requires_thumbnail': True,
                'supports_captions': False,
                'thumbnail_resolution': '640x640',
                'adaptation_rules': {
                    'audio': {
                        'format': 'mp3',
                        'bitrate': '320k',
                        'sample_rate': '44100'
                    }
                }
            }
        }
    
    async def _initialize_platform_adapters(self) -> None:
        """Initialize platform adapters."""        # This would initialize actual platform adapters
        for platform in self.platform_configs:
            self.platform_adapters[platform] = type('MockPlatformAdapter', (), {
                'publish_content': self._mock_platform_publish
            })()
    
    async def _mock_platform_publish(self, publication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock platform publication for testing."""        await asyncio.sleep(1)  # Simulate upload time
        
        return {
            'success': True,
            'platform_id': f"mock_{uuid4()}",
            'platform_url': f"https://mock-{publication_data.get('platform', 'platform')}.com/content/{uuid4()}",
            'analytics_data': {
                'views': 0,
                'likes': 0,
                'shares': 0,
                'comments': 0
            }
        }
    
    async def _test_platform_connections(self) -> None:
        """Test connections to all configured platforms."""        for platform, adapter in self.platform_adapters.items():
            try:
                if hasattr(adapter, 'test_connection'):
                    connected = await adapter.test_connection()
                    self.platform_connections[platform] = connected
                else:
                    self.platform_connections[platform] = True  # Mock connection
                    
                self.logger.info(f"Platform {platform} connection: {'OK' if self.platform_connections[platform] else 'FAILED'}")
                
            except Exception as e:
                self.logger.error(f"Failed to test connection for {platform}: {e}")
                self.platform_connections[platform] = False
    
    async def _shutdown_platform_adapters(self) -> None:
        """Shutdown platform adapters."""        for platform, adapter in self.platform_adapters.items():
            if hasattr(adapter, 'shutdown'):
                try:
                    await adapter.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down {platform} adapter: {e}")
    
    async def _cleanup_temp_files(self) -> None:
        """Clean up all temporary files."""        if self.temp_dir.exists():
            try:
                for file_path in self.temp_dir.glob('*'):
                    if file_path.is_file():
                        file_path.unlink()
                
                self.logger.info("Temporary files cleaned up")
                
            except Exception as e:
                self.logger.error(f"Error cleaning up temporary files: {e}")
    
    async def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""        try:
            return Path(file_path).stat().st_size
        except (OSError, FileNotFoundError):
            return 0
    
    def _update_platform_metrics(self, platform: str, success: bool) -> None:
        """Update platform-specific metrics."""        if platform not in self.metrics['platform_metrics']:
            self.metrics['platform_metrics'][platform] = {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0
            }
        
        platform_metrics = self.metrics['platform_metrics'][platform]
        platform_metrics['total'] += 1
        
        if success:
            platform_metrics['successful'] += 1
        else:
            platform_metrics['failed'] += 1
        
        platform_metrics['success_rate'] = platform_metrics['successful'] / platform_metrics['total']
    
    def get_publication_status(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """Get status of a publication request."""        # Check active publications
        if request_id in self.active_publications:
            request = self.active_publications[request_id]
            return {
                'status': 'active',
                'request': request,
                'started_at': request.created_at
            }
        
        # Check completed publications
        if request_id in self.completed_publications:
            result = self.completed_publications[request_id]
            return {
                'status': 'completed',
                'result': result
            }
        
        return None
    
    def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """Get status for a specific platform."""        return {
            'platform': platform,
            'connected': self.platform_connections.get(platform, False),
            'config': self.platform_configs.get(platform, {}),
            'metrics': self.metrics['platform_metrics'].get(platform, {}),
            'adapter_available': platform in self.platform_adapters
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""        return {
            **self.metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'active_publications': len(self.active_publications),
            'completed_publications': len(self.completed_publications),
            'platform_connections': self.platform_connections.copy(),
            'system_status': {
                'initialized': self.is_initialized,
                'temp_dir': str(self.temp_dir),
                'max_concurrent_uploads': self.max_concurrent_uploads
            }
        }


# Custom exceptions
class SecurityError(Exception):
    """Content security scan failed."""    pass


class ComplianceError(Exception):
    """Content compliance validation failed."""    pass


class ProcessingError(Exception):
    """Content processing failed."""    pass
