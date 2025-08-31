"""Distribution - Multi-Platform Content Distribution Engine
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, modification, distribution, or theft of this code 
without explicit written permission from the author is strictly prohibited
and will result in severe legal consequences under German and international law.

Email: mlaiel@live.de

This module provides comprehensive multi-platform content distribution including
automated publishing, metadata optimization, and cross-platform analytics.
"""
import logging
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import requests
from urllib.parse import urljoin
import base64

from .signal_processing import AudioData

logger = logging.getLogger(__name__)

class DistributionChannel(Enum):
    """Distribution channels/platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    TIDAL = "tidal"
    DEEZER = "deezer"
    PANDORA = "pandora"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DISTROKID = "distrokid"
    CD_BABY = "cd_baby"
    TUNECORE = "tunecore"
    REVERBNATION = "reverbnation"
    AUDIOMACK = "audiomack"
    NAPSTER = "napster"
    IHEARTRADIO = "iheartradio"
    SHAZAM = "shazam"
    BEATPORT = "beatport"
    TRAXSOURCE = "traxsource"
    JUNO_DOWNLOAD = "juno_download"

class DistributionStatus(Enum):
    """Distribution status"""    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    TAKEDOWN = "takedown"
    UNDER_REVIEW = "under_review"

class ContentFormat(Enum):
    """Content formats for distribution"""    AUDIO = "audio"
    VIDEO = "video"
    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
    PLAYLIST = "playlist"
    PODCAST = "podcast"

class ReleaseType(Enum):
    """Types of releases"""    SINGLE = "single"
    EP = "ep"
    ALBUM = "album"
    COMPILATION = "compilation"
    REMIX = "remix"
    REMASTER = "remaster"
    LIVE = "live"
    SOUNDTRACK = "soundtrack"

@dataclass
class PlatformCredentials:
    """Platform API credentials"""    platform: DistributionChannel
    client_id: str
    client_secret: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_base_url: str = ""
    sandbox_mode: bool = True
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionMetadata:
    """Content metadata for distribution"""    title: str
    artist_name: str
    album_name: Optional[str] = None
    genre: str = "Electronic"
    sub_genre: Optional[str] = None
    release_date: Optional[datetime] = None
    description: str = ""
    tags: List[str] = field(default_factory=list)
    language: str = "en"
    isrc_code: Optional[str] = None
    upc_code: Optional[str] = None
    copyright_notice: str = ""
    producer: Optional[str] = None
    composer: Optional[str] = None
    publisher: Optional[str] = None
    record_label: Optional[str] = None
    duration_seconds: int = 0
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[int] = None  # 1-10 scale
    explicit_content: bool = False
    cover_art_url: Optional[str] = None
    preview_url: Optional[str] = None
    lyrics: Optional[str] = None
    credits: List[Dict[str, str]] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionSettings:
    """Distribution configuration settings"""    channels: List[DistributionChannel]
    release_type: ReleaseType = ReleaseType.SINGLE
    content_format: ContentFormat = ContentFormat.AUDIO
    auto_publish: bool = True
    pre_release_date: Optional[datetime] = None
    take_down_date: Optional[datetime] = None
    territories: List[str] = field(default_factory=lambda: ["WW"])  # Worldwide
    pricing_tier: str = "standard"
    allow_preview: bool = True
    sync_licensing: bool = True
    content_id_enabled: bool = True
    monetization_enabled: bool = True
    analytics_enabled: bool = True
    social_media_promotion: bool = False
    playlist_pitching: bool = True
    radio_promotion: bool = False
    store_pre_orders: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Distribution operation result"""    distribution_id: str
    platform: DistributionChannel
    status: DistributionStatus
    content_url: Optional[str] = None
    platform_id: Optional[str] = None  # Platform-specific content ID
    submission_date: datetime = field(default_factory=datetime.utcnow)
    published_date: Optional[datetime] = None
    estimated_live_date: Optional[datetime] = None
    take_down_date: Optional[datetime] = None
    streams_count: int = 0
    downloads_count: int = 0
    revenue_generated: float = 0.0
    currency: str = "USD"
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    platform_response: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    success: bool = True
    metadata_used: Optional[DistributionMetadata] = None

@dataclass
class CrossPlatformAnalytics:
    """Cross-platform analytics aggregation"""    content_id: str
    total_streams: int = 0
    total_downloads: int = 0
    total_revenue: float = 0.0
    currency: str = "USD"
    platform_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    geographic_data: Dict[str, int] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    time_series_data: List[Dict[str, Any]] = field(default_factory=list)
    top_performing_platforms: List[str] = field(default_factory=list)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    report_period: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.utcnow(), datetime.utcnow()))

class MultiPlatformDistributor:
    """    Advanced Multi-Platform Content Distribution Engine
    
    Provides comprehensive distribution including:
    - Automated multi-platform publishing
    - Metadata optimization for each platform
    - Cross-platform analytics aggregation
    - Revenue tracking and reporting
    - Content lifecycle management
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        
        # Platform configurations
        self.platform_configs = self._setup_platform_configurations()
        self.platform_credentials: Dict[DistributionChannel, PlatformCredentials] = {}
        
        # Distribution tracking
        self.distribution_results: Dict[str, List[DistributionResult]] = {}
        self.analytics_cache: Dict[str, CrossPlatformAnalytics] = {}
        
        # Load platform credentials from config
        self._load_platform_credentials()
        
        # Platform-specific requirements
        self.platform_requirements = self._define_platform_requirements()
        
        # SEO optimization settings
        self.seo_optimization_enabled = True
        self.metadata_templates = self._load_metadata_templates()
        
        self.logger.info("MultiPlatformDistributor initialized successfully")
    
    def _setup_platform_configurations(self) -> Dict[DistributionChannel, Dict[str, Any]]:
        """Setup platform-specific configurations"""        return {
            DistributionChannel.SPOTIFY: {
                'api_base': 'https://api.spotify.com/v1',
                'auth_url': 'https://accounts.spotify.com/api/token',
                'supported_formats': ['mp3', 'wav', 'flac'],
                'max_file_size_mb': 200,
                'metadata_requirements': ['title', 'artist_name', 'isrc_code'],
                'review_time_days': 1,
                'territories_supported': 'worldwide',
                'monetization': True
            },
            DistributionChannel.APPLE_MUSIC: {
                'api_base': 'https://api.music.apple.com/v1',
                'auth_url': 'https://appleid.apple.com/auth/token',
                'supported_formats': ['aac', 'alac', 'mp3'],
                'max_file_size_mb': 300,
                'metadata_requirements': ['title', 'artist_name', 'upc_code'],
                'review_time_days': 2,
                'territories_supported': 'worldwide',
                'monetization': True
            },
            DistributionChannel.YOUTUBE_MUSIC: {
                'api_base': 'https://www.googleapis.com/youtube/v3',
                'auth_url': 'https://oauth2.googleapis.com/token',
                'supported_formats': ['mp3', 'wav', 'aac'],
                'max_file_size_mb': 2048,  # 2GB for video
                'metadata_requirements': ['title', 'artist_name', 'description'],
                'review_time_days': 0,  # Immediate
                'territories_supported': 'worldwide',
                'monetization': True
            },
            DistributionChannel.SOUNDCLOUD: {
                'api_base': 'https://api.soundcloud.com',
                'auth_url': 'https://api.soundcloud.com/oauth2/token',
                'supported_formats': ['mp3', 'wav', 'flac', 'aac'],
                'max_file_size_mb': 5000,  # 5GB for Pro
                'metadata_requirements': ['title', 'artist_name'],
                'review_time_days': 0,  # Immediate
                'territories_supported': 'worldwide',
                'monetization': True
            },
            DistributionChannel.BANDCAMP: {
                'api_base': 'https://bandcamp.com/api',
                'supported_formats': ['flac', 'wav', 'mp3'],
                'max_file_size_mb': 700,
                'metadata_requirements': ['title', 'artist_name', 'album_name'],
                'review_time_days': 0,
                'territories_supported': 'worldwide',
                'monetization': True
            }
        }
    
    def _load_platform_credentials(self):
        """Load platform credentials from configuration"""        credentials_config = self.config.get('platform_credentials', {})
        
        for platform_name, creds in credentials_config.items():
            try:
                platform = DistributionChannel(platform_name.lower())
                credentials = PlatformCredentials(
                    platform=platform,
                    client_id=creds.get('client_id', ''),
                    client_secret=creds.get('client_secret', ''),
                    api_key=creds.get('api_key'),
                    api_base_url=creds.get('api_base_url', ''),
                    sandbox_mode=creds.get('sandbox_mode', True)
                )
                self.platform_credentials[platform] = credentials
                
            except ValueError:
                self.logger.warning(f"Unknown platform in credentials: {platform_name}")
    
    def _define_platform_requirements(self) -> Dict[DistributionChannel, Dict[str, Any]]:
        """Define platform-specific requirements"""        return {
            DistributionChannel.SPOTIFY: {
                'min_duration_seconds': 30,
                'max_duration_seconds': 3600,
                'required_cover_art': True,
                'cover_art_min_size': (640, 640),
                'explicit_content_allowed': True,
                'preview_length_seconds': 30
            },
            DistributionChannel.APPLE_MUSIC: {
                'min_duration_seconds': 30,
                'max_duration_seconds': 3600,
                'required_cover_art': True,
                'cover_art_min_size': (3000, 3000),
                'explicit_content_allowed': True,
                'preview_length_seconds': 30
            },
            DistributionChannel.YOUTUBE_MUSIC: {
                'min_duration_seconds': 10,
                'max_duration_seconds': 43200,  # 12 hours
                'required_cover_art': False,
                'explicit_content_allowed': True,
                'thumbnail_required': True
            },
            DistributionChannel.SOUNDCLOUD: {
                'min_duration_seconds': 1,
                'max_duration_seconds': 21600,  # 6 hours
                'required_cover_art': False,
                'explicit_content_allowed': True,
                'waveform_generation': True
            }
        }
    
    def _load_metadata_templates(self) -> Dict[DistributionChannel, Dict[str, str]]:
        """Load platform-specific metadata templates"""        return {
            DistributionChannel.SPOTIFY: {
                'title_format': "{title}",
                'description_format': "{description}",
                'tags_format': "#{tag}"
            },
            DistributionChannel.YOUTUBE_MUSIC: {
                'title_format': "{title} - {artist_name}",
                'description_format': "{description}\n\nArtist: {artist_name}\nGenre: {genre}\n\n{copyright_notice}",
                'tags_format': "{tag}"
            },
            DistributionChannel.SOUNDCLOUD: {
                'title_format': "{title}",
                'description_format': "{description}\n\n#musicproduction #{genre} #{mood}",
                'tags_format': "{tag}"
            }
        }
    
    async def distribute_to_platform(
        self,
        audio_data: AudioData,
        platform: DistributionChannel,
        metadata: DistributionMetadata,
        settings: Optional[DistributionSettings] = None
    ) -> DistributionResult:
        """        Distribute content to specific platform
        
        Args:
            audio_data: Audio content to distribute
            platform: Target distribution platform
            metadata: Content metadata
            settings: Distribution settings
            
        Returns:
            DistributionResult with submission details
        """        distribution_id = str(uuid.uuid4())
        
        try:
            # Validate platform support
            if platform not in self.platform_configs:
                raise ValueError(f"Platform not supported: {platform.value}")
            
            # Check credentials
            credentials = self.platform_credentials.get(platform)
            if not credentials:
                raise ValueError(f"No credentials configured for platform: {platform.value}")
            
            # Validate content requirements
            validation_result = await self._validate_content_requirements(
                audio_data, platform, metadata
            )
            
            if not validation_result['valid']:
                return DistributionResult(
                    distribution_id=distribution_id,
                    platform=platform,
                    status=DistributionStatus.FAILED,
                    error_message=f"Content validation failed: {validation_result['errors']}",
                    success=False
                )
            
            # Optimize metadata for platform
            optimized_metadata = await self._optimize_metadata_for_platform(
                metadata, platform
            )
            
            # Prepare content for upload
            prepared_content = await self._prepare_content_for_platform(
                audio_data, platform, optimized_metadata
            )
            
            # Authenticate with platform
            auth_token = await self._authenticate_with_platform(platform, credentials)
            
            # Upload content
            upload_result = await self._upload_content_to_platform(
                prepared_content,
                platform,
                optimized_metadata,
                auth_token
            )
            
            # Create distribution result
            result = DistributionResult(
                distribution_id=distribution_id,
                platform=platform,
                status=DistributionStatus.PROCESSING if upload_result['success'] else DistributionStatus.FAILED,
                platform_id=upload_result.get('platform_id'),
                platform_response=upload_result.get('response', {}),
                error_message=upload_result.get('error'),
                success=upload_result['success'],
                metadata_used=optimized_metadata,
                estimated_live_date=self._calculate_estimated_live_date(platform)
            )
            
            # Store result
            if audio_data.metadata.get('fingerprint_id'):
                fingerprint_id = audio_data.metadata['fingerprint_id']
                if fingerprint_id not in self.distribution_results:
                    self.distribution_results[fingerprint_id] = []
                self.distribution_results[fingerprint_id].append(result)
            
            # Start monitoring if successful
            if result.success and result.status == DistributionStatus.PROCESSING:
                asyncio.create_task(
                    self._monitor_distribution_status(result, credentials)
                )
            
            self.logger.info(f"Distribution submitted to {platform.value}: {distribution_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Distribution to {platform.value} failed: {str(e)}")
            
            return DistributionResult(
                distribution_id=distribution_id,
                platform=platform,
                status=DistributionStatus.FAILED,
                error_message=str(e),
                success=False
            )
    
    async def distribute_to_multiple_platforms(
        self,
        audio_data: AudioData,
        metadata: DistributionMetadata,
        settings: DistributionSettings
    ) -> List[DistributionResult]:
        """Distribute content to multiple platforms simultaneously"""        results = []
        
        # Create distribution tasks for each platform
        distribution_tasks = []
        
        for platform in settings.channels:
            task = self.distribute_to_platform(
                audio_data, platform, metadata, settings
            )
            distribution_tasks.append(task)
        
        # Execute distributions concurrently
        results = await asyncio.gather(*distribution_tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                platform = settings.channels[i]
                error_result = DistributionResult(
                    distribution_id=str(uuid.uuid4()),
                    platform=platform,
                    status=DistributionStatus.FAILED,
                    error_message=str(result),
                    success=False
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        self.logger.info(f"Multi-platform distribution completed: {len(processed_results)} platforms")
        
        return processed_results
    
    async def _validate_content_requirements(
        self,
        audio_data: AudioData,
        platform: DistributionChannel,
        metadata: DistributionMetadata
    ) -> Dict[str, Any]:
        """Validate content meets platform requirements"""        errors = []
        platform_config = self.platform_configs.get(platform, {})
        platform_requirements = self.platform_requirements.get(platform, {})
        
        # Check duration requirements
        if 'min_duration_seconds' in platform_requirements:
            min_duration = platform_requirements['min_duration_seconds']
            if metadata.duration_seconds < min_duration:
                errors.append(f"Duration too short: {metadata.duration_seconds}s < {min_duration}s")
        
        if 'max_duration_seconds' in platform_requirements:
            max_duration = platform_requirements['max_duration_seconds']
            if metadata.duration_seconds > max_duration:
                errors.append(f"Duration too long: {metadata.duration_seconds}s > {max_duration}s")
        
        # Check required metadata fields
        required_metadata = platform_config.get('metadata_requirements', [])
        for field in required_metadata:
            if not getattr(metadata, field, None):
                errors.append(f"Required metadata field missing: {field}")
        
        # Check cover art requirements
        if platform_requirements.get('required_cover_art') and not metadata.cover_art_url:
            errors.append("Cover art is required for this platform")
        
        # Check file format
        supported_formats = platform_config.get('supported_formats', [])
        if audio_data.format.value not in supported_formats:
            errors.append(f"Audio format not supported: {audio_data.format.value}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _optimize_metadata_for_platform(
        self,
        metadata: DistributionMetadata,
        platform: DistributionChannel
    ) -> DistributionMetadata:
        """Optimize metadata for specific platform requirements"""        optimized = metadata  # Start with original metadata
        
        if not self.seo_optimization_enabled:
            return optimized
        
        platform_template = self.metadata_templates.get(platform, {})
        
        # Optimize title
        if 'title_format' in platform_template:
            title_format = platform_template['title_format']
            optimized.title = title_format.format(
                title=metadata.title,
                artist_name=metadata.artist_name,
                genre=metadata.genre
            )
        
        # Optimize description
        if 'description_format' in platform_template:
            description_format = platform_template['description_format']
            optimized.description = description_format.format(
                description=metadata.description or "New release",
                artist_name=metadata.artist_name,
                genre=metadata.genre,
                copyright_notice=metadata.copyright_notice or f"© {datetime.now().year} {metadata.artist_name}",
                mood=metadata.mood or "energetic"
            )
        
        # Optimize tags for platform
        if platform == DistributionChannel.YOUTUBE_MUSIC:
            # YouTube benefits from more detailed tags
            optimized.tags = self._enhance_tags_for_youtube(metadata)
        elif platform == DistributionChannel.SOUNDCLOUD:
            # SoundCloud benefits from hashtag-style tags
            optimized.tags = [f"#{tag.replace(' ', '')}" for tag in metadata.tags]
        
        # Platform-specific optimizations
        if platform == DistributionChannel.SPOTIFY:
            # Spotify prefers clean, standard metadata
            optimized.title = metadata.title.strip()
            optimized.artist_name = metadata.artist_name.strip()
        
        elif platform == DistributionChannel.APPLE_MUSIC:
            # Apple Music has strict metadata standards
            if not optimized.upc_code:
                optimized.upc_code = self._generate_upc_code()
        
        return optimized
    
    def _enhance_tags_for_youtube(self, metadata: DistributionMetadata) -> List[str]:
        """Enhance tags specifically for YouTube algorithm"""        enhanced_tags = metadata.tags.copy()
        
        # Add genre-related tags
        enhanced_tags.append(metadata.genre.lower())
        if metadata.sub_genre:
            enhanced_tags.append(metadata.sub_genre.lower())
        
        # Add mood/energy tags
        if metadata.mood:
            enhanced_tags.append(metadata.mood.lower())
        
        # Add instrument/production tags based on genre
        genre_instruments = {
            'electronic': ['synthesizer', 'drum machine', 'edm'],
            'rock': ['guitar', 'drums', 'bass'],
            'hip hop': ['beats', 'rap', 'hip hop'],
            'jazz': ['saxophone', 'piano', 'improvisation']
        }
        
        genre_lower = metadata.genre.lower()
        if genre_lower in genre_instruments:
            enhanced_tags.extend(genre_instruments[genre_lower])
        
        # Add year tag
        if metadata.release_date:
            enhanced_tags.append(str(metadata.release_date.year))
        
        # Remove duplicates and empty tags
        enhanced_tags = list(set([tag for tag in enhanced_tags if tag.strip()]))
        
        return enhanced_tags[:50]  # YouTube has a tag limit
    
    def _generate_upc_code(self) -> str:
        """Generate UPC code for releases"""        # This is a simplified UPC generation - in production, use proper UPC allocation
        import random
        upc = f"0{random.randint(10**11, 10**12-1)}"
        return upc
    
    async def _prepare_content_for_platform(
        self,
        audio_data: AudioData,
        platform: DistributionChannel,
        metadata: DistributionMetadata
    ) -> Dict[str, Any]:
        """Prepare content for platform-specific upload"""        prepared = {
            'audio_data': audio_data,
            'metadata': metadata,
            'platform': platform
        }
        
        platform_config = self.platform_configs.get(platform, {})
        
        # Convert to platform-preferred format if needed
        preferred_formats = platform_config.get('supported_formats', [])
        if preferred_formats and audio_data.format.value not in preferred_formats:
            # In production, implement audio format conversion
            self.logger.warning(f"Audio format conversion needed for {platform.value}")
        
        # Check file size limits
        max_size_mb = platform_config.get('max_file_size_mb', 200)
        # In production, implement file size checking and compression if needed
        
        # Generate platform-specific files
        if platform == DistributionChannel.YOUTUBE_MUSIC:
            # YouTube might need video generation from audio + cover art
            prepared['needs_video_generation'] = True
        
        return prepared
    
    async def _authenticate_with_platform(
        self,
        platform: DistributionChannel,
        credentials: PlatformCredentials
    ) -> str:
        """Authenticate with platform and get access token"""        platform_config = self.platform_configs.get(platform, {})
        auth_url = platform_config.get('auth_url')
        
        if not auth_url:
            return "mock_token"  # For platforms without API access
        
        # Mock authentication (in production, implement real OAuth flows)
        if platform == DistributionChannel.SPOTIFY:
            return await self._authenticate_spotify(credentials, auth_url)
        elif platform == DistributionChannel.YOUTUBE_MUSIC:
            return await self._authenticate_youtube(credentials, auth_url)
        elif platform == DistributionChannel.SOUNDCLOUD:
            return await self._authenticate_soundcloud(credentials, auth_url)
        else:
            return "mock_token"
    
    async def _authenticate_spotify(
        self,
        credentials: PlatformCredentials,
        auth_url: str
    ) -> str:
        """Authenticate with Spotify API"""        # Mock Spotify authentication
        return f"spotify_token_{credentials.client_id}"
    
    async def _authenticate_youtube(
        self,
        credentials: PlatformCredentials,
        auth_url: str
    ) -> str:
        """Authenticate with YouTube API"""        # Mock YouTube authentication
        return f"youtube_token_{credentials.client_id}"
    
    async def _authenticate_soundcloud(
        self,
        credentials: PlatformCredentials,
        auth_url: str
    ) -> str:
        """Authenticate with SoundCloud API"""        # Mock SoundCloud authentication
        return f"soundcloud_token_{credentials.client_id}"
    
    async def _upload_content_to_platform(
        self,
        prepared_content: Dict[str, Any],
        platform: DistributionChannel,
        metadata: DistributionMetadata,
        auth_token: str
    ) -> Dict[str, Any]:
        """Upload content to specific platform"""        try:
            # Mock upload process (in production, implement real API calls)
            platform_id = f"{platform.value}_{uuid.uuid4().hex[:8]}"
            
            # Simulate upload success with some randomness for testing
            import random
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                return {
                    'success': True,
                    'platform_id': platform_id,
                    'response': {
                        'status': 'uploaded',
                        'review_status': 'pending' if platform in [DistributionChannel.APPLE_MUSIC] else 'approved',
                        'estimated_live_time': self._calculate_estimated_live_date(platform).isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f"Upload failed to {platform.value}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_estimated_live_date(self, platform: DistributionChannel) -> datetime:
        """Calculate when content will go live on platform"""        platform_config = self.platform_configs.get(platform, {})
        review_time_days = platform_config.get('review_time_days', 1)
        
        return datetime.utcnow() + timedelta(days=review_time_days)
    
    async def _monitor_distribution_status(
        self,
        result: DistributionResult,
        credentials: PlatformCredentials
    ):
        """Monitor distribution status and update result"""        max_checks = 10
        check_interval = 300  # 5 minutes
        
        for check_count in range(max_checks):
            try:
                await asyncio.sleep(check_interval)
                
                # Mock status check (in production, implement real API calls)
                import random
                
                if random.random() > 0.8:  # 20% chance of going live each check
                    result.status = DistributionStatus.PUBLISHED
                    result.published_date = datetime.utcnow()
                    result.content_url = f"https://{result.platform.value}.com/track/{result.platform_id}"
                    
                    self.logger.info(f"Content went live on {result.platform.value}: {result.distribution_id}")
                    break
                
            except Exception as e:
                self.logger.error(f"Status monitoring error: {str(e)}")
        
        # If still processing after all checks, mark as published (assumption)
        if result.status == DistributionStatus.PROCESSING:
            result.status = DistributionStatus.PUBLISHED
            result.published_date = datetime.utcnow()
    
    async def get_cross_platform_analytics(
        self,
        content_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> CrossPlatformAnalytics:
        """Get aggregated analytics across all platforms"""        # Check cache first
        cache_key = f"{content_id}_{start_date.date()}_{end_date.date()}"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        # Aggregate analytics from all platforms
        analytics = CrossPlatformAnalytics(
            content_id=content_id,
            report_period=(start_date, end_date)
        )
        
        # Get distribution results for content
        distribution_results = self.distribution_results.get(content_id, [])
        
        for result in distribution_results:
            if result.status == DistributionStatus.PUBLISHED:
                # Mock analytics data (in production, fetch from platform APIs)
                platform_analytics = await self._fetch_platform_analytics(
                    result, start_date, end_date
                )
                
                # Aggregate data
                analytics.total_streams += platform_analytics.get('streams', 0)
                analytics.total_downloads += platform_analytics.get('downloads', 0)
                analytics.total_revenue += platform_analytics.get('revenue', 0.0)
                
                # Platform breakdown
                analytics.platform_breakdown[result.platform.value] = platform_analytics
        
        # Determine top performing platforms
        platform_performance = [
            (platform, data.get('revenue', 0))
            for platform, data in analytics.platform_breakdown.items()
        ]
        platform_performance.sort(key=lambda x: x[1], reverse=True)
        analytics.top_performing_platforms = [p[0] for p in platform_performance]
        
        # Cache result
        self.analytics_cache[cache_key] = analytics
        
        return analytics
    
    async def _fetch_platform_analytics(
        self,
        result: DistributionResult,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch analytics from specific platform"""        # Mock analytics (in production, implement real API calls)
        import random
        
        days_diff = (end_date - start_date).days
        
        return {
            'streams': random.randint(100, 10000) * days_diff,
            'downloads': random.randint(10, 500) * days_diff,
            'revenue': random.uniform(5.0, 500.0) * days_diff,
            'engagement_rate': random.uniform(0.1, 0.8),
            'skip_rate': random.uniform(0.1, 0.4),
            'completion_rate': random.uniform(0.6, 0.95),
            'geographic_data': {
                'US': random.randint(100, 5000),
                'DE': random.randint(50, 2000),
                'GB': random.randint(50, 1500),
                'CA': random.randint(25, 1000)
            }
        }
    
    def get_distribution_results(self, content_id: str) -> List[DistributionResult]:
        """Get distribution results for content"""        return self.distribution_results.get(content_id, [])
    
    async def update_content_metadata(
        self,
        content_id: str,
        platform: DistributionChannel,
        updated_metadata: DistributionMetadata
    ) -> bool:
        """Update content metadata on platform"""        try:
            # Find distribution result
            results = self.distribution_results.get(content_id, [])
            platform_result = None
            
            for result in results:
                if result.platform == platform:
                    platform_result = result
                    break
            
            if not platform_result:
                return False
            
            # Mock metadata update (in production, implement API call)
            platform_result.metadata_used = updated_metadata
            
            self.logger.info(f"Metadata updated on {platform.value} for {content_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Metadata update failed: {str(e)}")
            return False
    
    async def takedown_content(
        self,
        content_id: str,
        platform: Optional[DistributionChannel] = None,
        reason: str = ""
    ) -> List[bool]:
        """Takedown content from platform(s)"""        results = []
        
        distribution_results = self.distribution_results.get(content_id, [])
        
        for result in distribution_results:
            if platform is None or result.platform == platform:
                try:
                    # Mock takedown (in production, implement API call)
                    result.status = DistributionStatus.TAKEDOWN
                    result.take_down_date = datetime.utcnow()
                    
                    self.logger.info(f"Content taken down from {result.platform.value}: {content_id}")
                    
                    results.append(True)
                    
                except Exception as e:
                    self.logger.error(f"Takedown failed on {result.platform.value}: {str(e)}")
                    results.append(False)
        
        return results
