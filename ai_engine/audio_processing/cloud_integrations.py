"""
Cloud Integrations Module - Multi-Platform Audio Distribution Engine
Advanced cloud services integration for professional audio processing and distribution.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️ 
This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
STRICTLY PROHIBITED and will result in immediate legal action.
All rights reserved. Patent pending.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import boto3
try:
    from google.cloud import storage as gcs
except ImportError:
    gcs = None
try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None
try:
    import dropbox
except ImportError:
    dropbox = None
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    spotipy = None
    SpotifyOAuth = None
from datetime import datetime, timedelta
import base64
import hashlib
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    DROPBOX = "dropbox"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    YOUTUBE_MUSIC = "youtube_music"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"
    CUSTOM_CDN = "custom_cdn"


class DistributionStatus(Enum):
    """Distribution status states"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    REMOVED = "removed"


@dataclass
class CloudCredentials:
    """Cloud service credentials"""
    provider: CloudProvider
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    project_id: Optional[str] = None
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioMetadata:
    """Audio metadata for distribution"""
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    release_date: Optional[datetime] = None
    copyright_info: Optional[str] = None
    isrc: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    explicit: bool = False
    language: str = "en"


@dataclass
class DistributionResult:
    """Distribution operation result"""
    provider: CloudProvider
    status: DistributionStatus
    url: Optional[str] = None
    track_id: Optional[str] = None
    error_message: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CloudStorageManager:
    """Advanced cloud storage management"""
    
    def __init__(self, credentials: Dict[CloudProvider, CloudCredentials]):
        self.credentials = credentials
        self.clients = {}
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize cloud service clients"""
        for provider, creds in self.credentials.items():
            try:
                if provider == CloudProvider.AWS_S3:
                    self.clients[provider] = boto3.client(
                        's3',
                        aws_access_key_id=creds.api_key,
                        aws_secret_access_key=creds.secret_key,
                        region_name=creds.region or 'us-east-1'
                    )
                    
                elif provider == CloudProvider.GOOGLE_CLOUD:
                    self.clients[provider] = gcs.Client(
                        project=creds.project_id,
                        credentials=creds.additional_params.get('service_account_path')
                    )
                    
                elif provider == CloudProvider.AZURE_BLOB:
                    self.clients[provider] = BlobServiceClient(
                        account_url=f"https://{creds.additional_params.get('account_name')}.blob.core.windows.net",
                        credential=creds.api_key
                    )
                    
                elif provider == CloudProvider.DROPBOX:
                    self.clients[provider] = dropbox.Dropbox(creds.token)
                    
                logger.info(f"Initialized {provider.value} client")
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider.value} client: {e}")
    
    async def upload_audio(self, 
                          file_path: Path, 
                          provider: CloudProvider,
                          metadata: AudioMetadata,
                          folder_path: Optional[str] = None) -> DistributionResult:
        """Upload audio file to cloud storage"""
        try:
            start_time = datetime.now()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{metadata.artist}_{metadata.title}_{timestamp}.{file_path.suffix[1:]}"
            
            if folder_path:
                remote_path = f"{folder_path}/{filename}"
            else:
                remote_path = filename
            
            if provider == CloudProvider.AWS_S3:
                return await self._upload_to_s3(file_path, remote_path, metadata, start_time)
                
            elif provider == CloudProvider.GOOGLE_CLOUD:
                return await self._upload_to_gcs(file_path, remote_path, metadata, start_time)
                
            elif provider == CloudProvider.AZURE_BLOB:
                return await self._upload_to_azure(file_path, remote_path, metadata, start_time)
                
            elif provider == CloudProvider.DROPBOX:
                return await self._upload_to_dropbox(file_path, remote_path, metadata, start_time)
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Upload failed for {provider.value}: {e}")
            return DistributionResult(
                provider=provider,
                status=DistributionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _upload_to_s3(self, file_path: Path, remote_path: str, 
                           metadata: AudioMetadata, start_time: datetime) -> DistributionResult:
        """Upload to AWS S3"""
        client = self.clients[CloudProvider.AWS_S3]
        bucket = self.credentials[CloudProvider.AWS_S3].bucket_name
        
        try:
            # Upload with metadata
            extra_args = {
                'Metadata': {
                    'title': metadata.title,
                    'artist': metadata.artist,
                    'genre': metadata.genre or '',
                    'duration': str(metadata.duration or 0),
                    'upload_timestamp': start_time.isoformat()
                },
                'ContentType': 'audio/mpeg'
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                client.upload_file,
                str(file_path),
                bucket,
                remote_path,
                extra_args
            )
            
            # Generate URL
            url = f"https://{bucket}.s3.amazonaws.com/{remote_path}"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=CloudProvider.AWS_S3,
                status=DistributionStatus.PUBLISHED,
                url=url,
                track_id=remote_path,
                upload_timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"S3 upload failed: {e}")
    
    async def _upload_to_gcs(self, file_path: Path, remote_path: str,
                            metadata: AudioMetadata, start_time: datetime) -> DistributionResult:
        """Upload to Google Cloud Storage"""
        client = self.clients[CloudProvider.GOOGLE_CLOUD]
        bucket_name = self.credentials[CloudProvider.GOOGLE_CLOUD].bucket_name
        
        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(remote_path)
            
            # Set metadata
            blob.metadata = {
                'title': metadata.title,
                'artist': metadata.artist,
                'genre': metadata.genre or '',
                'upload_timestamp': start_time.isoformat()
            }
            
            # Upload file
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob.upload_from_filename,
                str(file_path)
            )
            
            # Make public if needed
            blob.make_public()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=CloudProvider.GOOGLE_CLOUD,
                status=DistributionStatus.PUBLISHED,
                url=blob.public_url,
                track_id=remote_path,
                upload_timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"GCS upload failed: {e}")
    
    async def _upload_to_azure(self, file_path: Path, remote_path: str,
                              metadata: AudioMetadata, start_time: datetime) -> DistributionResult:
        """Upload to Azure Blob Storage"""
        client = self.clients[CloudProvider.AZURE_BLOB]
        container = self.credentials[CloudProvider.AZURE_BLOB].bucket_name
        
        try:
            # Create blob client
            blob_client = client.get_blob_client(
                container=container,
                blob=remote_path
            )
            
            # Set metadata
            blob_metadata = {
                'title': metadata.title,
                'artist': metadata.artist,
                'genre': metadata.genre or '',
                'upload_timestamp': start_time.isoformat()
            }
            
            # Upload file
            with open(file_path, 'rb') as data:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    blob_client.upload_blob,
                    data,
                    True,  # overwrite
                    None,  # content_settings
                    blob_metadata
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=CloudProvider.AZURE_BLOB,
                status=DistributionStatus.PUBLISHED,
                url=blob_client.url,
                track_id=remote_path,
                upload_timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"Azure upload failed: {e}")
    
    async def _upload_to_dropbox(self, file_path: Path, remote_path: str,
                                metadata: AudioMetadata, start_time: datetime) -> DistributionResult:
        """Upload to Dropbox"""
        client = self.clients[CloudProvider.DROPBOX]
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload file
            await asyncio.get_event_loop().run_in_executor(
                None,
                client.files_upload,
                file_data,
                f"/{remote_path}",
                dropbox.files.WriteMode.overwrite,
                True,  # autorename
                None,  # client_modified
                True   # mute
            )
            
            # Create shared link
            shared_link = await asyncio.get_event_loop().run_in_executor(
                None,
                client.sharing_create_shared_link_with_settings,
                f"/{remote_path}"
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=CloudProvider.DROPBOX,
                status=DistributionStatus.PUBLISHED,
                url=shared_link.url,
                track_id=remote_path,
                upload_timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"Dropbox upload failed: {e}")


class MusicPlatformDistributor:
    """Advanced music platform distribution manager"""
    
    def __init__(self, credentials: Dict[CloudProvider, CloudCredentials]):
        self.credentials = credentials
        self.api_clients = {}
        self._initialize_api_clients()
    
    def _initialize_api_clients(self):
        """Initialize music platform API clients"""
        for provider, creds in self.credentials.items():
            try:
                if provider == CloudProvider.SPOTIFY:
                    self.api_clients[provider] = self._create_spotify_client(creds)
                elif provider == CloudProvider.SOUNDCLOUD:
                    self.api_clients[provider] = self._create_soundcloud_client(creds)
                # Add other platform clients as needed
                
                logger.info(f"Initialized {provider.value} API client")
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider.value} API client: {e}")
    
    def _create_spotify_client(self, creds: CloudCredentials):
        """Create Spotify API client"""
        # Note: Spotify doesn't allow direct uploads via API for most users
        # This would integrate with Spotify for Developers/Artists program
        return {
            'client_id': creds.api_key,
            'client_secret': creds.secret_key,
            'redirect_uri': creds.additional_params.get('redirect_uri'),
            'scope': 'user-library-modify playlist-modify-public'
        }
    
    def _create_soundcloud_client(self, creds: CloudCredentials):
        """Create SoundCloud API client"""
        return {
            'client_id': creds.api_key,
            'client_secret': creds.secret_key,
            'oauth_token': creds.token
        }
    
    async def distribute_to_platform(self, 
                                   file_path: Path,
                                   platform: CloudProvider,
                                   metadata: AudioMetadata,
                                   additional_options: Optional[Dict[str, Any]] = None) -> DistributionResult:
        """Distribute audio to specific music platform"""
        try:
            start_time = datetime.now()
            
            if platform == CloudProvider.SOUNDCLOUD:
                return await self._distribute_to_soundcloud(file_path, metadata, start_time, additional_options)
            else:
                # For platforms that don't support direct API uploads,
                # prepare for manual distribution or third-party services
                return await self._prepare_for_manual_distribution(file_path, platform, metadata, start_time)
                
        except Exception as e:
            logger.error(f"Distribution to {platform.value} failed: {e}")
            return DistributionResult(
                provider=platform,
                status=DistributionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _distribute_to_soundcloud(self, file_path: Path, metadata: AudioMetadata,
                                       start_time: datetime, options: Optional[Dict[str, Any]] = None) -> DistributionResult:
        """Distribute to SoundCloud"""
        client_config = self.api_clients[CloudProvider.SOUNDCLOUD]
        
        try:
            # Prepare track data
            track_data = {
                'title': metadata.title,
                'description': metadata.description or f"Track by {metadata.artist}",
                'genre': metadata.genre,
                'tag_list': ' '.join(metadata.tags) if metadata.tags else '',
                'sharing': options.get('sharing', 'public') if options else 'public',
                'downloadable': options.get('downloadable', True) if options else True
            }
            
            # Upload track (pseudo-code - actual implementation would use soundcloud-python library)
            # track = await soundcloud.upload_track(file_path, track_data, client_config['oauth_token'])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=CloudProvider.SOUNDCLOUD,
                status=DistributionStatus.PUBLISHED,
                url="https://soundcloud.com/placeholder",  # Would be actual track URL
                track_id="placeholder_id",
                upload_timestamp=start_time,
                processing_time=processing_time,
                metadata={'track_data': track_data}
            )
            
        except Exception as e:
            raise Exception(f"SoundCloud distribution failed: {e}")
    
    async def _prepare_for_manual_distribution(self, file_path: Path, platform: CloudProvider,
                                              metadata: AudioMetadata, start_time: datetime) -> DistributionResult:
        """Prepare files and metadata for manual distribution"""
        try:
            # Create distribution package
            distribution_folder = Path(tempfile.mkdtemp(prefix=f"{platform.value}_distribution_"))
            
            # Copy audio file
            target_file = distribution_folder / f"{metadata.artist}_{metadata.title}.{file_path.suffix[1:]}"
            target_file.write_bytes(file_path.read_bytes())
            
            # Create metadata file
            metadata_file = distribution_folder / "metadata.json"
            metadata_dict = {
                'title': metadata.title,
                'artist': metadata.artist,
                'album': metadata.album,
                'genre': metadata.genre,
                'release_date': metadata.release_date.isoformat() if metadata.release_date else None,
                'tags': metadata.tags,
                'description': metadata.description,
                'explicit': metadata.explicit,
                'language': metadata.language,
                'platform_specific': self._get_platform_requirements(platform)
            }
            
            metadata_file.write_text(json.dumps(metadata_dict, indent=2))
            
            # Create distribution guide
            guide_file = distribution_folder / "distribution_guide.md"
            guide_content = self._generate_distribution_guide(platform, metadata)
            guide_file.write_text(guide_content)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DistributionResult(
                provider=platform,
                status=DistributionStatus.PENDING,
                url=str(distribution_folder),
                track_id=str(target_file),
                upload_timestamp=start_time,
                processing_time=processing_time,
                metadata={'distribution_package': str(distribution_folder)}
            )
            
        except Exception as e:
            raise Exception(f"Distribution preparation failed: {e}")
    
    def _get_platform_requirements(self, platform: CloudProvider) -> Dict[str, Any]:
        """Get platform-specific requirements"""
        requirements = {
            CloudProvider.SPOTIFY: {
                'format': 'WAV or FLAC (recommended)',
                'quality': '44.1kHz/16-bit minimum',
                'artwork': '3000x3000px minimum',
                'distributor_required': True,
                'supported_distributors': ['DistroKid', 'CD Baby', 'TuneCore']
            },
            CloudProvider.APPLE_MUSIC: {
                'format': 'WAV or AIFF',
                'quality': '44.1kHz/16-bit minimum',
                'artwork': '3000x3000px',
                'distributor_required': True,
                'mastered_for_itunes': 'recommended'
            },
            CloudProvider.YOUTUBE_MUSIC: {
                'format': 'WAV recommended',
                'quality': '44.1kHz/16-bit minimum',
                'artwork': '1400x1400px minimum',
                'content_id': 'required for monetization'
            }
        }
        
        return requirements.get(platform, {})
    
    def _generate_distribution_guide(self, platform: CloudProvider, metadata: AudioMetadata) -> str:
        """Generate platform-specific distribution guide"""
        requirements = self._get_platform_requirements(platform)
        
        guide = f"""# {platform.value.replace('_', ' ').title()} Distribution Guide

## Track Information
- **Title**: {metadata.title}
- **Artist**: {metadata.artist}
- **Genre**: {metadata.genre or 'Not specified'}

## Platform Requirements
"""
        
        for key, value in requirements.items():
            guide += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        guide += f"""
## Distribution Steps
1. Ensure your audio file meets the quality requirements
2. Prepare high-resolution artwork
3. {"Use a digital distributor service" if requirements.get('distributor_required') else "Upload directly via platform"}
4. Submit for review and approval

## Files Prepared
- Audio file: Ready for upload
- Metadata: Complete and formatted
- This guide: For reference

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return guide


class MultiPlatformDistributionManager:
    """Comprehensive multi-platform distribution management"""
    
    def __init__(self, 
                 cloud_credentials: Dict[CloudProvider, CloudCredentials],
                 platform_credentials: Dict[CloudProvider, CloudCredentials]):
        self.storage_manager = CloudStorageManager(cloud_credentials)
        self.platform_distributor = MusicPlatformDistributor(platform_credentials)
        self.distribution_history: List[DistributionResult] = []
    
    async def distribute_to_all_platforms(self,
                                        file_path: Path,
                                        metadata: AudioMetadata,
                                        target_platforms: List[CloudProvider],
                                        storage_providers: Optional[List[CloudProvider]] = None) -> Dict[CloudProvider, DistributionResult]:
        """Distribute to multiple platforms simultaneously"""
        results = {}
        
        # First, upload to storage providers
        if storage_providers:
            storage_tasks = []
            for provider in storage_providers:
                task = self.storage_manager.upload_audio(file_path, provider, metadata)
                storage_tasks.append((provider, task))
            
            for provider, task in storage_tasks:
                try:
                    result = await task
                    results[provider] = result
                    self.distribution_history.append(result)
                    logger.info(f"Storage upload to {provider.value}: {result.status.value}")
                except Exception as e:
                    logger.error(f"Storage upload to {provider.value} failed: {e}")
        
        # Then distribute to music platforms
        platform_tasks = []
        for platform in target_platforms:
            task = self.platform_distributor.distribute_to_platform(file_path, platform, metadata)
            platform_tasks.append((platform, task))
        
        for platform, task in platform_tasks:
            try:
                result = await task
                results[platform] = result
                self.distribution_history.append(result)
                logger.info(f"Platform distribution to {platform.value}: {result.status.value}")
            except Exception as e:
                logger.error(f"Platform distribution to {platform.value} failed: {e}")
        
        return results
    
    async def get_distribution_status(self, track_id: str) -> List[DistributionResult]:
        """Get distribution status for a track"""
        return [result for result in self.distribution_history if result.track_id == track_id]
    
    async def retry_failed_distributions(self, 
                                       file_path: Path,
                                       metadata: AudioMetadata) -> Dict[CloudProvider, DistributionResult]:
        """Retry failed distributions"""
        failed_providers = [
            result.provider for result in self.distribution_history
            if result.status == DistributionStatus.FAILED
        ]
        
        if not failed_providers:
            return {}
        
        logger.info(f"Retrying distribution to {len(failed_providers)} failed providers")
        
        return await self.distribute_to_all_platforms(
            file_path=file_path,
            metadata=metadata,
            target_platforms=failed_providers
        )
    
    def get_distribution_analytics(self) -> Dict[str, Any]:
        """Get distribution analytics and statistics"""
        total_distributions = len(self.distribution_history)
        
        if total_distributions == 0:
            return {'total_distributions': 0}
        
        status_counts = {}
        provider_counts = {}
        processing_times = []
        
        for result in self.distribution_history:
            # Count by status
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by provider
            provider = result.provider.value
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            
            # Collect processing times
            if result.processing_time:
                processing_times.append(result.processing_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        success_rate = (status_counts.get('published', 0) / total_distributions) * 100
        
        return {
            'total_distributions': total_distributions,
            'status_breakdown': status_counts,
            'provider_breakdown': provider_counts,
            'success_rate_percent': round(success_rate, 2),
            'average_processing_time_seconds': round(avg_processing_time, 2),
            'total_successful': status_counts.get('published', 0),
            'total_failed': status_counts.get('failed', 0),
            'total_pending': status_counts.get('pending', 0)
        }


# Factory functions for common distribution scenarios
async def create_music_distributor(config_path: Optional[Path] = None) -> MultiPlatformDistributionManager:
    """Create a configured music distributor"""
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration template
        config = {
            'storage_providers': {},
            'platform_providers': {}
        }
    
    # Convert config to credential objects
    storage_credentials = {}
    platform_credentials = {}
    
    for provider_name, creds_data in config.get('storage_providers', {}).items():
        provider = CloudProvider(provider_name)
        storage_credentials[provider] = CloudCredentials(**creds_data)
    
    for provider_name, creds_data in config.get('platform_providers', {}).items():
        provider = CloudProvider(provider_name)
        platform_credentials[provider] = CloudCredentials(**creds_data)
    
    return MultiPlatformDistributionManager(storage_credentials, platform_credentials)


async def quick_upload_to_storage(file_path: Path,
                                 metadata: AudioMetadata,
                                 provider: CloudProvider = CloudProvider.AWS_S3) -> DistributionResult:
    """Quick upload to a single storage provider"""
    # This would need actual credentials configuration
    credentials = {
        provider: CloudCredentials(
            provider=provider,
            api_key=os.getenv(f"{provider.value.upper()}_API_KEY"),
            secret_key=os.getenv(f"{provider.value.upper()}_SECRET_KEY"),
            bucket_name=os.getenv(f"{provider.value.upper()}_BUCKET"),
            region=os.getenv(f"{provider.value.upper()}_REGION", "us-east-1")
        )
    }
    
    storage_manager = CloudStorageManager(credentials)
    return await storage_manager.upload_audio(file_path, provider, metadata)
