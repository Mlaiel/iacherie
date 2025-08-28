"""
Data Loaders Module
Author: Fahed Mlaiel <mlaiel@live.de>

Advanced data loading systems for distributed content delivery,
platform integration, and intelligent storage management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

# Cloud storage
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs

# Database
import psycopg2
from sqlalchemy.ext.asyncio import AsyncSession
import redis
import pymongo

# Platform APIs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..core.exceptions import LoaderError, StorageError, PlatformError
from ..core.metrics import MetricsCollector
from ..core.config import LoaderConfig
from ..utils.decorators import monitor_performance, retry_on_failure
from ..utils.encryption import EncryptionManager
from ..utils.compression import CompressionManager


@dataclass
class LoadingJob:
    """Data loading job specification."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_data: Dict[str, Any] = field(default_factory=dict)
    destination: str = ""
    platform: str = ""
    loading_options: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3


class DistributedLoader:
    """
    High-performance distributed content loader with intelligent
    load balancing and multi-cloud storage support.
    """
    
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("distributed_loader")
        
        # Initialize storage clients
        self.storage_clients = {}
        self.encryption_manager = EncryptionManager(config.encryption_config)
        self.compression_manager = CompressionManager()
        
        # Initialize distributed infrastructure
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True
        )
        
        self.worker_pool = ThreadPoolExecutor(max_workers=config.max_concurrent_uploads)
        
        self._initialize_storage_clients()
    
    def _initialize_storage_clients(self):
        """Initialize cloud storage clients."""
        
        # AWS S3
        if self.config.aws_config:
            self.storage_clients['s3'] = boto3.client(
                's3',
                aws_access_key_id=self.config.aws_config['access_key'],
                aws_secret_access_key=self.config.aws_config['secret_key'],
                region_name=self.config.aws_config['region']
            )
        
        # Azure Blob Storage
        if self.config.azure_config:
            self.storage_clients['azure'] = BlobServiceClient(
                account_url=f"https://{self.config.azure_config['account_name']}.blob.core.windows.net",
                credential=self.config.azure_config['account_key']
            )
        
        # Google Cloud Storage
        if self.config.gcp_config:
            self.storage_clients['gcs'] = gcs.Client.from_service_account_json(
                self.config.gcp_config['credentials_path']
            )
    
    @monitor_performance
    async def create_distribution_package(
        self,
        content_data: Dict[str, Any],
        platform: str,
        package_id: str
    ) -> Dict[str, Any]:
        """
        Create optimized distribution package for specific platform.
        
        Args:
            content_data: Content data with optimizations
            platform: Target platform identifier
            package_id: Unique package identifier
            
        Returns:
            Distribution package information
        """
        
        package_info = {
            'package_id': package_id,
            'platform': platform,
            'created_at': datetime.utcnow().isoformat(),
            'content_metadata': content_data.get('metadata', {}),
            'distribution_urls': {},
            'verification_data': {}
        }
        
        try:
            # Prepare content for distribution
            prepared_content = await self._prepare_content_for_distribution(
                content_data,
                platform
            )
            
            # Upload to distributed storage
            storage_results = await self._upload_to_distributed_storage(
                prepared_content,
                package_id,
                platform
            )
            
            package_info['distribution_urls'] = storage_results
            
            # Generate verification data
            verification_data = await self._generate_verification_data(
                prepared_content,
                storage_results
            )
            
            package_info['verification_data'] = verification_data
            
            # Cache package information
            await self._cache_package_info(package_id, package_info)
            
            self.metrics.increment('packages_created')
            self.logger.info(f"Distribution package {package_id} created for {platform}")
            
            return package_info
            
        except Exception as e:
            self.metrics.increment('package_creation_errors')
            self.logger.error(f"Package creation failed for {package_id}: {e}")
            raise LoaderError(f"Failed to create distribution package: {e}")
    
    async def _prepare_content_for_distribution(
        self,
        content_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Prepare content data for platform-specific distribution."""
        
        prepared_content = content_data.copy()
        
        # Apply platform-specific optimizations
        if platform == 'youtube':
            prepared_content = await self._optimize_for_youtube(prepared_content)
        elif platform == 'instagram':
            prepared_content = await self._optimize_for_instagram(prepared_content)
        elif platform == 'tiktok':
            prepared_content = await self._optimize_for_tiktok(prepared_content)
        elif platform == 'spotify':
            prepared_content = await self._optimize_for_spotify(prepared_content)
        
        # Apply compression if enabled
        if self.config.enable_compression:
            prepared_content['data'] = await self.compression_manager.compress(
                prepared_content['data'],
                content_data.get('type', 'binary')
            )
            prepared_content['compression_applied'] = True
        
        # Apply encryption if enabled
        if self.config.enable_encryption:
            prepared_content['data'] = await self.encryption_manager.encrypt(
                prepared_content['data']
            )
            prepared_content['encryption_applied'] = True
        
        return prepared_content
    
    async def _optimize_for_youtube(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply YouTube-specific optimizations."""
        
        if content.get('type') == 'video':
            # YouTube video optimizations
            content['youtube_metadata'] = {
                'title': content.get('title', ''),
                'description': content.get('description', ''),
                'tags': content.get('tags', []),
                'category': content.get('category', ''),
                'privacy': content.get('privacy', 'private'),
                'thumbnail_url': content.get('thumbnail_url', '')
            }
        
        return content
    
    async def _optimize_for_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Instagram-specific optimizations."""
        
        if content.get('type') in ['image', 'video']:
            # Instagram format optimizations
            content['instagram_metadata'] = {
                'caption': content.get('caption', ''),
                'hashtags': content.get('hashtags', []),
                'location': content.get('location', ''),
                'user_tags': content.get('user_tags', [])
            }
        
        return content
    
    async def _optimize_for_tiktok(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply TikTok-specific optimizations."""
        
        if content.get('type') == 'video':
            # TikTok video optimizations
            content['tiktok_metadata'] = {
                'description': content.get('description', ''),
                'hashtags': content.get('hashtags', []),
                'effects': content.get('effects', []),
                'music_id': content.get('music_id', '')
            }
        
        return content
    
    async def _optimize_for_spotify(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Spotify-specific optimizations."""
        
        if content.get('type') == 'audio':
            # Spotify audio optimizations
            content['spotify_metadata'] = {
                'title': content.get('title', ''),
                'artist': content.get('artist', ''),
                'album': content.get('album', ''),
                'genre': content.get('genre', ''),
                'release_date': content.get('release_date', ''),
                'isrc': content.get('isrc', '')
            }
        
        return content
    
    @retry_on_failure(max_retries=3)
    async def _upload_to_distributed_storage(
        self,
        content: Dict[str, Any],
        package_id: str,
        platform: str
    ) -> Dict[str, str]:
        """Upload content to distributed storage systems."""
        
        storage_urls = {}
        upload_tasks = []
        
        # Determine optimal storage strategy
        storage_strategy = self._determine_storage_strategy(content, platform)
        
        for storage_type in storage_strategy:
            if storage_type in self.storage_clients:
                task = asyncio.create_task(
                    self._upload_to_storage(
                        content,
                        package_id,
                        storage_type
                    )
                )
                upload_tasks.append((storage_type, task))
        
        # Wait for all uploads to complete
        for storage_type, task in upload_tasks:
            try:
                url = await task
                storage_urls[storage_type] = url
                self.metrics.increment(f'uploads_successful_{storage_type}')
                
            except Exception as e:
                self.logger.error(f"Upload to {storage_type} failed: {e}")
                self.metrics.increment(f'uploads_failed_{storage_type}')
                
                # Continue with other storage systems
                continue
        
        if not storage_urls:
            raise StorageError("All storage uploads failed")
        
        return storage_urls
    
    def _determine_storage_strategy(
        self,
        content: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Determine optimal storage strategy based on content and platform."""
        
        content_type = content.get('type', '')
        content_size = content.get('size', 0)
        
        # Strategy based on content type and size
        if content_type == 'video' or content_size > 100 * 1024 * 1024:  # > 100MB
            # Large files: prefer S3 or GCS
            return ['s3', 'gcs', 'azure']
        elif platform in ['instagram', 'tiktok']:
            # Social media: prefer faster CDN-enabled storage
            return ['azure', 's3']
        else:
            # Default strategy
            return ['s3', 'azure', 'gcs']
    
    async def _upload_to_storage(
        self,
        content: Dict[str, Any],
        package_id: str,
        storage_type: str
    ) -> str:
        """Upload content to specific storage system."""
        
        if storage_type == 's3':
            return await self._upload_to_s3(content, package_id)
        elif storage_type == 'azure':
            return await self._upload_to_azure(content, package_id)
        elif storage_type == 'gcs':
            return await self._upload_to_gcs(content, package_id)
        else:
            raise StorageError(f"Unsupported storage type: {storage_type}")
    
    async def _upload_to_s3(self, content: Dict[str, Any], package_id: str) -> str:
        """Upload content to AWS S3."""
        
        bucket_name = self.config.aws_config['bucket']
        key = f"content/{package_id}/{content.get('filename', 'content')}"
        
        # Upload using asyncio
        loop = asyncio.get_event_loop()
        
        def upload():
            self.storage_clients['s3'].put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content['data'],
                ContentType=content.get('mime_type', 'application/octet-stream'),
                Metadata={
                    'package_id': package_id,
                    'content_type': content.get('type', ''),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
        
        await loop.run_in_executor(self.worker_pool, upload)
        
        # Generate public URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        return url
    
    async def _upload_to_azure(self, content: Dict[str, Any], package_id: str) -> str:
        """Upload content to Azure Blob Storage."""
        
        container_name = self.config.azure_config['container']
        blob_name = f"content/{package_id}/{content.get('filename', 'content')}"
        
        blob_client = self.storage_clients['azure'].get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        # Upload using asyncio
        loop = asyncio.get_event_loop()
        
        def upload():
            blob_client.upload_blob(
                content['data'],
                overwrite=True,
                metadata={
                    'package_id': package_id,
                    'content_type': content.get('type', ''),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
        
        await loop.run_in_executor(self.worker_pool, upload)
        
        return blob_client.url
    
    async def _upload_to_gcs(self, content: Dict[str, Any], package_id: str) -> str:
        """Upload content to Google Cloud Storage."""
        
        bucket_name = self.config.gcp_config['bucket']
        blob_name = f"content/{package_id}/{content.get('filename', 'content')}"
        
        bucket = self.storage_clients['gcs'].bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Upload using asyncio
        loop = asyncio.get_event_loop()
        
        def upload():
            blob.upload_from_string(
                content['data'],
                content_type=content.get('mime_type', 'application/octet-stream')
            )
            
            # Set metadata
            blob.metadata = {
                'package_id': package_id,
                'content_type': content.get('type', ''),
                'uploaded_at': datetime.utcnow().isoformat()
            }
            blob.patch()
        
        await loop.run_in_executor(self.worker_pool, upload)
        
        return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"


class PlatformLoader:
    """
    Specialized loader for platform-specific content delivery
    with API integration and automated publishing workflows.
    """
    
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("platform_loader")
        
        # Initialize platform APIs
        self.platform_apis = {}
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self._initialize_platform_apis()
    
    def _initialize_platform_apis(self):
        """Initialize platform-specific API clients."""
        
        # YouTube API
        if self.config.youtube_config:
            self.platform_apis['youtube'] = YouTubeAPI(
                self.config.youtube_config,
                self.session
            )
        
        # Instagram API
        if self.config.instagram_config:
            self.platform_apis['instagram'] = InstagramAPI(
                self.config.instagram_config,
                self.session
            )
        
        # TikTok API
        if self.config.tiktok_config:
            self.platform_apis['tiktok'] = TikTokAPI(
                self.config.tiktok_config,
                self.session
            )
        
        # Spotify API
        if self.config.spotify_config:
            self.platform_apis['spotify'] = SpotifyAPI(
                self.config.spotify_config,
                self.session
            )
    
    @monitor_performance
    async def load_to_platform(
        self,
        content_package: Dict[str, Any],
        platform: str,
        publishing_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Load content to specific platform with automated publishing.
        
        Args:
            content_package: Distribution package data
            platform: Target platform identifier
            publishing_options: Platform-specific publishing options
            
        Returns:
            Publishing results with platform response
        """
        
        if platform not in self.platform_apis:
            raise PlatformError(f"Platform {platform} not configured")
        
        platform_api = self.platform_apis[platform]
        
        try:
            # Prepare content for platform
            prepared_content = await self._prepare_platform_content(
                content_package,
                platform,
                publishing_options
            )
            
            # Upload content to platform
            upload_result = await platform_api.upload_content(prepared_content)
            
            # Publish content if configured
            if publishing_options.get('auto_publish', False):
                publish_result = await platform_api.publish_content(
                    upload_result['content_id'],
                    publishing_options
                )
                upload_result['publish_result'] = publish_result
            
            # Track publishing metrics
            self.metrics.increment(f'content_loaded_{platform}')
            self.logger.info(f"Content loaded to {platform}: {upload_result.get('content_id')}")
            
            return {
                'platform': platform,
                'status': 'success',
                'platform_content_id': upload_result.get('content_id'),
                'platform_url': upload_result.get('url'),
                'upload_result': upload_result,
                'loaded_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.metrics.increment(f'content_load_errors_{platform}')
            self.logger.error(f"Platform loading failed for {platform}: {e}")
            raise PlatformError(f"Failed to load content to {platform}: {e}")
    
    async def _prepare_platform_content(
        self,
        content_package: Dict[str, Any],
        platform: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare content for platform-specific requirements."""
        
        prepared = content_package.copy()
        
        # Apply platform-specific content preparation
        if platform == 'youtube':
            prepared = await self._prepare_youtube_content(prepared, options)
        elif platform == 'instagram':
            prepared = await self._prepare_instagram_content(prepared, options)
        elif platform == 'tiktok':
            prepared = await self._prepare_tiktok_content(prepared, options)
        elif platform == 'spotify':
            prepared = await self._prepare_spotify_content(prepared, options)
        
        return prepared


class StorageLoader:
    """
    High-performance storage loader with intelligent data management,
    caching strategies, and automated backup systems.
    """
    
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("storage_loader")
        
        # Initialize storage systems
        self.database_pool = None
        self.redis_client = None
        self.mongo_client = None
        
        self._initialize_storage_systems()
    
    def _initialize_storage_systems(self):
        """Initialize various storage systems."""
        
        # PostgreSQL connection pool
        if self.config.postgres_config:
            # Initialize PostgreSQL async connection pool
            try:
                import asyncpg
                self.postgres_pool = None  # Will be initialized in async context
                self.postgres_config = {
                    'host': self.config.postgres_config['host'],
                    'port': self.config.postgres_config['port'],
                    'database': self.config.postgres_config['database'],
                    'user': self.config.postgres_config['user'],
                    'password': self.config.postgres_config['password'],
                    'min_size': self.config.postgres_config.get('min_pool_size', 5),
                    'max_size': self.config.postgres_config.get('max_pool_size', 20)
                }
                self.logger.info("PostgreSQL connection config initialized")
            except ImportError:
                self.logger.warning("asyncpg not available, PostgreSQL loader disabled")
                self.postgres_pool = None
        
        # Redis for caching
        if self.config.redis_config:
            self.redis_client = redis.Redis(
                host=self.config.redis_config['host'],
                port=self.config.redis_config['port'],
                db=self.config.redis_config['db'],
                decode_responses=True
            )
        
        # MongoDB for document storage
        if self.config.mongo_config:
            self.mongo_client = pymongo.MongoClient(
                self.config.mongo_config['connection_string']
            )
    
    @monitor_performance
    async def load_to_database(
        self,
        data: Dict[str, Any],
        table_name: str,
        loading_strategy: str = 'insert'
    ) -> Dict[str, Any]:
        """
        Load data to database with intelligent loading strategies.
        
        Args:
            data: Data to load
            table_name: Target table name
            loading_strategy: Loading strategy (insert, upsert, bulk)
            
        Returns:
            Loading result information
        """
        
        try:
            if loading_strategy == 'insert':
                result = await self._insert_data(data, table_name)
            elif loading_strategy == 'upsert':
                result = await self._upsert_data(data, table_name)
            elif loading_strategy == 'bulk':
                result = await self._bulk_load_data(data, table_name)
            else:
                raise LoaderError(f"Unsupported loading strategy: {loading_strategy}")
            
            self.metrics.increment(f'database_loads_{loading_strategy}')
            return result
            
        except Exception as e:
            self.metrics.increment('database_load_errors')
            self.logger.error(f"Database loading failed: {e}")
            raise LoaderError(f"Database loading failed: {e}")
    
    async def _insert_data(self, data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """Insert data using standard INSERT operation."""
        
        # Implementation would use actual database connection
        # This is a simplified example
        
        return {
            'operation': 'insert',
            'table': table_name,
            'rows_affected': 1,
            'execution_time_ms': 50
        }
    
    async def _upsert_data(self, data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """Insert or update data using UPSERT operation."""
        
        # Implementation would use actual database connection
        # This is a simplified example
        
        return {
            'operation': 'upsert',
            'table': table_name,
            'rows_affected': 1,
            'execution_time_ms': 75
        }
    
    async def _bulk_load_data(self, data: List[Dict[str, Any]], table_name: str) -> Dict[str, Any]:
        """Bulk load data for high-performance scenarios."""
        
        # Implementation would use actual database connection
        # This is a simplified example
        
        return {
            'operation': 'bulk_load',
            'table': table_name,
            'rows_affected': len(data) if isinstance(data, list) else 1,
            'execution_time_ms': 200
        }


class AnalyticsLoader:
    """
    Specialized loader for analytics data with real-time streaming
    and time-series optimization.
    """
    
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("analytics_loader")
        
        # Initialize analytics storage
        self.time_series_db = None
        self.elasticsearch_client = None
        
        self._initialize_analytics_storage()
    
    def _initialize_analytics_storage(self):
        """Initialize analytics-specific storage systems."""
        
        # InfluxDB for time-series data
        if self.config.influxdb_config:
            # Initialize InfluxDB client
            try:
                from influxdb_client import InfluxDBClient
                self.influxdb_client = InfluxDBClient(
                    url=self.config.influxdb_config['url'],
                    token=self.config.influxdb_config['token'],
                    org=self.config.influxdb_config['org']
                )
                self.influxdb_bucket = self.config.influxdb_config['bucket']
                self.logger.info("InfluxDB client initialized")
            except ImportError:
                self.logger.warning("InfluxDB client not available, time-series storage disabled")
                self.influxdb_client = None
        
        # Elasticsearch for full-text search and analytics
        if self.config.elasticsearch_config:
            # Initialize Elasticsearch client
            try:
                from elasticsearch import AsyncElasticsearch
                self.elasticsearch_client = AsyncElasticsearch(
                    hosts=[self.config.elasticsearch_config['host']],
                    http_auth=(
                        self.config.elasticsearch_config.get('username'),
                        self.config.elasticsearch_config.get('password')
                    ),
                    verify_certs=self.config.elasticsearch_config.get('verify_certs', True),
                    ssl_context=self.config.elasticsearch_config.get('ssl_context')
                )
                self.elasticsearch_index = self.config.elasticsearch_config.get('index', 'analytics')
                self.logger.info("Elasticsearch client initialized")
            except ImportError:
                self.logger.warning("Elasticsearch client not available, search analytics disabled")
                self.elasticsearch_client = None
    
    @monitor_performance
    async def load_analytics_data(
        self,
        analytics_data: Dict[str, Any],
        data_type: str = 'event'
    ) -> Dict[str, Any]:
        """
        Load analytics data with optimized storage strategies.
        
        Args:
            analytics_data: Analytics data to load
            data_type: Type of analytics data (event, metric, log)
            
        Returns:
            Loading result with indexing information
        """
        
        try:
            # Enrich analytics data
            enriched_data = await self._enrich_analytics_data(analytics_data)
            
            # Route to appropriate storage
            if data_type == 'time_series':
                result = await self._load_time_series_data(enriched_data)
            elif data_type == 'search_index':
                result = await self._load_search_data(enriched_data)
            else:
                result = await self._load_event_data(enriched_data)
            
            self.metrics.increment(f'analytics_loads_{data_type}')
            return result
            
        except Exception as e:
            self.metrics.increment('analytics_load_errors')
            self.logger.error(f"Analytics loading failed: {e}")
            raise LoaderError(f"Analytics loading failed: {e}")
    
    async def _enrich_analytics_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich analytics data with additional metadata."""
        
        enriched = data.copy()
        enriched.update({
            'loaded_at': datetime.utcnow().isoformat(),
            'loader_version': '2.0.0',
            'data_hash': hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        })
        
        return enriched
    
    async def _initialize_postgres_pool(self):
        """Initialize PostgreSQL connection pool asynchronously"""
        if self.postgres_config and not self.postgres_pool:
            try:
                import asyncpg
                self.postgres_pool = await asyncpg.create_pool(**self.postgres_config)
                self.logger.info("✅ PostgreSQL connection pool initialized")
                return True
            except Exception as e:
                self.logger.error(f"Failed to initialize PostgreSQL pool: {e}")
                return False
        return True
    
    async def _load_to_postgres(self, data: Dict[str, Any], table: str) -> bool:
        """Load data to PostgreSQL"""
        try:
            if not self.postgres_pool:
                await self._initialize_postgres_pool()
            
            if self.postgres_pool:
                async with self.postgres_pool.acquire() as conn:
                    # Generate INSERT query dynamically
                    columns = list(data.keys())
                    values = list(data.values())
                    placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
                    
                    query = f"""
                        INSERT INTO {table} ({', '.join(columns)}) 
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                    
                    await conn.execute(query, *values)
                    self.logger.debug(f"📊 Data loaded to PostgreSQL table {table}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"PostgreSQL load error: {e}")
            return False
    
    async def _load_to_influxdb(self, data: Dict[str, Any], measurement: str) -> bool:
        """Load time-series data to InfluxDB"""
        try:
            if self.influxdb_client:
                from influxdb_client.client.write_api import SYNCHRONOUS
                write_api = self.influxdb_client.write_api(write_option=SYNCHRONOUS)
                
                # Prepare data point
                point_data = {
                    'measurement': measurement,
                    'tags': data.get('tags', {}),
                    'fields': data.get('fields', {}),
                    'time': data.get('timestamp', datetime.utcnow())
                }
                
                write_api.write(bucket=self.influxdb_bucket, record=point_data)
                self.logger.debug(f"📈 Time-series data loaded to InfluxDB measurement {measurement}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"InfluxDB load error: {e}")
            return False
    
    async def _load_to_elasticsearch(self, data: Dict[str, Any], doc_type: str = '_doc') -> bool:
        """Load document data to Elasticsearch"""
        try:
            if self.elasticsearch_client:
                doc_id = data.get('id', str(uuid.uuid4()))
                
                await self.elasticsearch_client.index(
                    index=self.elasticsearch_index,
                    id=doc_id,
                    body=data,
                    doc_type=doc_type
                )
                
                self.logger.debug(f"🔍 Document loaded to Elasticsearch index {self.elasticsearch_index}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Elasticsearch load error: {e}")
            return False
    
    async def close_connections(self):
        """Close all storage connections gracefully"""
        try:
            # Close PostgreSQL pool
            if self.postgres_pool:
                await self.postgres_pool.close()
                self.logger.info("PostgreSQL pool closed")
            
            # Close InfluxDB client
            if self.influxdb_client:
                self.influxdb_client.close()
                self.logger.info("InfluxDB client closed")
            
            # Close Elasticsearch client
            if self.elasticsearch_client:
                await self.elasticsearch_client.close()
                self.logger.info("Elasticsearch client closed")
                
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")
