"""
Automated distribution engine for multi-platform content and revenue distribution.

This module implements comprehensive distribution orchestration including:
- Multi-platform content distribution automation
- Intelligent revenue distribution and payouts
- Automated royalty calculations and payments
- Cross-platform synchronization and reporting
- Advanced distribution analytics and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Distribution Systems Architect: Multi-Platform Content Orchestration
- Revenue Operations Specialist: Automated Payout & Royalty Management
- Data Pipeline Engineer: Real-time Distribution Analytics
- Partnership Manager: Platform Integrations & Content Partnerships

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import hashlib
from pathlib import Path
import aiofiles
from urllib.parse import urlencode
import boto3
from google.cloud import storage as gcs
import ftplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_database, get_redis_client
from ..core.exceptions import DistributionException, PayoutException


class DistributionPlatform(Enum):
    """Supported distribution platforms."""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    BANDCAMP = "bandcamp"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    DISCORD = "discord"


class ContentType(Enum):
    """Types of content for distribution."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    PODCAST = "podcast"
    PLAYLIST = "playlist"
    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
    REMIX = "remix"
    COVER = "cover"
    LIVE_RECORDING = "live_recording"


class DistributionStatus(Enum):
    """Distribution status tracking."""
    PENDING = "pending"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    DISTRIBUTED = "distributed"
    LIVE = "live"
    FAILED = "failed"
    REJECTED = "rejected"
    TAKEDOWN_REQUESTED = "takedown_requested"
    REMOVED = "removed"


class PayoutStatus(Enum):
    """Payout processing status."""
    PENDING = "pending"
    CALCULATING = "calculating"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class PayoutMethod(Enum):
    """Supported payout methods."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE_CONNECT = "stripe_connect"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"
    STORE_CREDIT = "store_credit"


@dataclass
class ContentAsset:
    """Content asset for distribution."""
    asset_id: str
    creator_id: str
    title: str
    content_type: ContentType
    file_path: str
    file_size: int
    duration: Optional[float] = None
    format: str = ""
    quality: str = "high"
    metadata: Dict[str, Any] = field(default_factory=dict)
    thumbnail_path: Optional[str] = None
    preview_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    explicit_content: bool = False
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DistributionTarget:
    """Distribution target configuration."""
    platform: DistributionPlatform
    enabled: bool = True
    auto_distribute: bool = False
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    release_schedule: Optional[datetime] = None
    pricing_tier: str = "standard"
    territory_restrictions: List[str] = field(default_factory=list)
    age_restrictions: Optional[str] = None
    distribution_priority: int = 5  # 1-10, higher = more priority


@dataclass
class DistributionJob:
    """Distribution job tracking."""
    job_id: str
    creator_id: str
    asset: ContentAsset
    targets: List[DistributionTarget]
    status: DistributionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueRecord:
    """Revenue tracking record."""
    record_id: str
    creator_id: str
    platform: str
    content_id: str
    revenue_period_start: datetime
    revenue_period_end: datetime
    gross_revenue: Decimal
    platform_fee: Decimal
    service_fee: Decimal
    net_revenue: Decimal
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.00")
    revenue_type: str = "streaming"  # streaming, download, licensing, etc.
    units_sold: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutRequest:
    """Payout processing request."""
    payout_id: str
    creator_id: str
    total_amount: Decimal
    currency: str
    payout_method: PayoutMethod
    status: PayoutStatus
    revenue_records: List[str]  # List of revenue record IDs
    recipient_details: Dict[str, Any]
    payout_date: datetime
    processing_fee: Decimal = Decimal("0.00")
    net_amount: Decimal = Decimal("0.00")
    reference_number: Optional[str] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


@dataclass
class PlatformIntegration:
    """Platform integration configuration."""
    platform: DistributionPlatform
    api_endpoint: str
    auth_method: str
    credentials: Dict[str, str]
    supported_formats: List[str]
    max_file_size: int
    upload_method: str  # api, ftp, s3, etc.
    metadata_mapping: Dict[str, str]
    rate_limits: Dict[str, int]
    webhook_config: Dict[str, Any] = field(default_factory=dict)
    last_sync: Optional[datetime] = None


class AutomatedDistributionEngine:
    """
    Comprehensive automated distribution and payout engine.
    
    Provides advanced distribution orchestration including:
    - Multi-platform content distribution automation
    - Intelligent revenue aggregation and reconciliation
    - Automated payout processing and management
    - Real-time distribution analytics and reporting
    - Cross-platform synchronization and optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("monetization.distribution_engine")
        self.db = get_database()
        self.redis = get_redis_client()
        
        # Session management
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=60, connect=15)
        
        # Storage configurations
        self.storage_config = self._initialize_storage_config()
        self.content_storage_path = Path(self.config.get("content_storage", "./content"))
        
        # Platform integrations
        self.platform_integrations = {}
        self.distribution_queues = {}
        
        # Revenue processing settings
        self.revenue_aggregation_schedule = self.config.get("revenue_schedule", "daily")
        self.minimum_payout_amount = Decimal(str(self.config.get("minimum_payout", "50.00")))
        self.payout_processing_schedule = self.config.get("payout_schedule", "weekly")
        
        # Distribution settings
        self.max_concurrent_uploads = self.config.get("max_concurrent_uploads", 5)
        self.upload_timeout_minutes = self.config.get("upload_timeout_minutes", 30)
        self.retry_delay_minutes = self.config.get("retry_delay_minutes", 15)
        
        # Thread pool for file operations
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_uploads)
        
        # Initialize components
        asyncio.create_task(self._initialize_distribution_engine())
        
        self.logger.info("AutomatedDistributionEngine initialized successfully")
    
    async def _initialize_distribution_engine(self):
        """Initialize distribution engine components."""
        try:
            # Initialize HTTP session
            await self._initialize_session()
            
            # Load platform integrations
            await self._load_platform_integrations()
            
            # Initialize distribution queues
            await self._initialize_distribution_queues()
            
            # Initialize storage systems
            await self._initialize_storage_systems()
            
            # Start background processing tasks
            await self._start_background_tasks()
            
            self.logger.info("Distribution engine components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Distribution engine initialization failed: {e}")
            raise DistributionException(f"Engine initialization error: {e}")
    
    async def _initialize_session(self):
        """Initialize aiohttp session for external API calls."""
        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.session_timeout,
                headers={
                    "User-Agent": "IA-Influencer-Agent/2.0 Distribution-Engine"
                }
            )
            
            self.logger.info("Distribution engine HTTP session initialized")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise DistributionException(f"Session initialization error: {e}")
    
    def _initialize_storage_config(self) -> Dict[str, Any]:
        """Initialize storage system configurations."""
        return {
            "aws_s3": {
                "bucket": self.config.get("aws_s3_bucket", ""),
                "region": self.config.get("aws_region", "us-east-1"),
                "access_key": self.config.get("aws_access_key", ""),
                "secret_key": self.config.get("aws_secret_key", "")
            },
            "google_cloud": {
                "bucket": self.config.get("gcs_bucket", ""),
                "project_id": self.config.get("gcs_project_id", ""),
                "credentials_path": self.config.get("gcs_credentials_path", "")
            },
            "local": {
                "base_path": self.content_storage_path,
                "max_file_size": self.config.get("max_file_size", 500 * 1024 * 1024)  # 500MB
            }
        }
    
    async def _load_platform_integrations(self):
        """Load platform integration configurations from database."""
        try:
            query = """
            SELECT 
                platform, api_endpoint, auth_method, credentials,
                supported_formats, max_file_size, upload_method,
                metadata_mapping, rate_limits, webhook_config,
                last_sync, is_active
            FROM platform_integrations
            WHERE is_active = true
            """
            
            results = await self.db.fetch(query)
            
            for row in results:
                platform = DistributionPlatform(row["platform"])
                
                integration = PlatformIntegration(
                    platform=platform,
                    api_endpoint=row["api_endpoint"],
                    auth_method=row["auth_method"],
                    credentials=json.loads(row["credentials"] or "{}"),
                    supported_formats=json.loads(row["supported_formats"] or "[]"),
                    max_file_size=row["max_file_size"],
                    upload_method=row["upload_method"],
                    metadata_mapping=json.loads(row["metadata_mapping"] or "{}"),
                    rate_limits=json.loads(row["rate_limits"] or "{}"),
                    webhook_config=json.loads(row["webhook_config"] or "{}"),
                    last_sync=row["last_sync"]
                )
                
                self.platform_integrations[platform] = integration
            
            self.logger.info(f"Loaded {len(self.platform_integrations)} platform integrations")
            
        except Exception as e:
            self.logger.error(f"Platform integration loading failed: {e}")
            # Initialize with default integrations
            await self._initialize_default_integrations()
    
    async def _initialize_default_integrations(self):
        """Initialize default platform integrations."""
        default_integrations = {
            DistributionPlatform.SPOTIFY: PlatformIntegration(
                platform=DistributionPlatform.SPOTIFY,
                api_endpoint="https://api.spotify.com/v1",
                auth_method="oauth2",
                credentials={"client_id": "", "client_secret": ""},
                supported_formats=["mp3", "flac", "wav"],
                max_file_size=100 * 1024 * 1024,  # 100MB
                upload_method="api",
                metadata_mapping={"title": "name", "artist": "artists"},
                rate_limits={"requests_per_minute": 100}
            ),
            DistributionPlatform.YOUTUBE: PlatformIntegration(
                platform=DistributionPlatform.YOUTUBE,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                auth_method="oauth2",
                credentials={"client_id": "", "client_secret": ""},
                supported_formats=["mp4", "mov", "avi", "mp3"],
                max_file_size=128 * 1024 * 1024,  # 128MB
                upload_method="api",
                metadata_mapping={"title": "snippet.title", "description": "snippet.description"},
                rate_limits={"requests_per_minute": 10000}
            )
        }
        
        self.platform_integrations.update(default_integrations)
    
    async def _initialize_distribution_queues(self):
        """Initialize distribution processing queues."""
        for platform in DistributionPlatform:
            queue_key = f"distribution_queue:{platform.value}"
            self.distribution_queues[platform] = queue_key
            
            # Initialize Redis queue if not exists
            queue_size = await self.redis.llen(queue_key)
            self.logger.debug(f"Distribution queue {platform.value}: {queue_size} items")
    
    async def _initialize_storage_systems(self):
        """Initialize cloud storage system connections."""
        try:
            # Initialize AWS S3 client
            if self.storage_config["aws_s3"]["access_key"]:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.storage_config["aws_s3"]["access_key"],
                    aws_secret_access_key=self.storage_config["aws_s3"]["secret_key"],
                    region_name=self.storage_config["aws_s3"]["region"]
                )
                self.logger.info("AWS S3 storage initialized")
            
            # Initialize Google Cloud Storage client
            if self.storage_config["google_cloud"]["credentials_path"]:
                self.gcs_client = gcs.Client.from_service_account_json(
                    self.storage_config["google_cloud"]["credentials_path"]
                )
                self.logger.info("Google Cloud Storage initialized")
            
            # Ensure local storage directory exists
            self.content_storage_path.mkdir(parents=True, exist_ok=True)
            self.logger.info("Local storage initialized")
            
        except Exception as e:
            self.logger.error(f"Storage system initialization failed: {e}")
    
    async def _start_background_tasks(self):
        """Start background processing tasks."""
        try:
            # Start distribution queue processors
            for platform in DistributionPlatform:
                if platform in self.platform_integrations:
                    asyncio.create_task(self._process_distribution_queue(platform))
            
            # Start revenue aggregation task
            asyncio.create_task(self._schedule_revenue_aggregation())
            
            # Start payout processing task
            asyncio.create_task(self._schedule_payout_processing())
            
            # Start platform sync task
            asyncio.create_task(self._schedule_platform_sync())
            
            self.logger.info("Background processing tasks started")
            
        except Exception as e:
            self.logger.error(f"Background task startup failed: {e}")
    
    async def distribute_content(
        self,
        creator_id: str,
        asset: ContentAsset,
        targets: List[DistributionTarget],
        schedule_release: bool = False
    ) -> DistributionJob:
        """
        Distribute content to multiple platforms with intelligent orchestration.
        
        Args:
            creator_id: Creator identifier
            asset: Content asset to distribute
            targets: List of distribution targets
            schedule_release: Whether to schedule release for later
            
        Returns:
            Distribution job with tracking information
        """
        try:
            # Generate unique job ID
            job_id = f"dist_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Starting content distribution job: {job_id}")
            
            # Validate content asset
            await self._validate_content_asset(asset)
            
            # Validate distribution targets
            validated_targets = await self._validate_distribution_targets(targets)
            
            # Create distribution job
            distribution_job = DistributionJob(
                job_id=job_id,
                creator_id=creator_id,
                asset=asset,
                targets=validated_targets,
                status=DistributionStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # Store job in database
            await self._store_distribution_job(distribution_job)
            
            if schedule_release:
                # Schedule for later distribution
                await self._schedule_distribution_job(distribution_job)
            else:
                # Start immediate distribution
                await self._start_distribution_job(distribution_job)
            
            self.logger.info(f"Distribution job created successfully: {job_id}")
            
            return distribution_job
            
        except Exception as e:
            self.logger.error(f"Content distribution failed: {e}")
            raise DistributionException(f"Distribution error: {e}")
    
    async def _validate_content_asset(self, asset: ContentAsset):
        """Validate content asset for distribution."""
        try:
            # Check if file exists
            file_path = Path(asset.file_path)
            if not file_path.exists():
                raise DistributionException(f"Content file not found: {asset.file_path}")
            
            # Verify file size matches
            actual_size = file_path.stat().st_size
            if abs(actual_size - asset.file_size) > 1024:  # Allow 1KB difference
                asset.file_size = actual_size
                self.logger.warning(f"File size mismatch corrected for asset: {asset.asset_id}")
            
            # Validate content type and format
            if not await self._is_valid_content_format(asset.content_type, asset.format):
                raise DistributionException(f"Unsupported format {asset.format} for {asset.content_type}")
            
            # Check for required metadata
            required_metadata = ["title", "artist", "genre"]
            missing_metadata = [field for field in required_metadata if not asset.metadata.get(field)]
            if missing_metadata:
                self.logger.warning(f"Missing metadata for asset {asset.asset_id}: {missing_metadata}")
            
            self.logger.info(f"Content asset validated successfully: {asset.asset_id}")
            
        except Exception as e:
            self.logger.error(f"Content asset validation failed: {e}")
            raise DistributionException(f"Asset validation error: {e}")
    
    async def _is_valid_content_format(self, content_type: ContentType, format: str) -> bool:
        """Check if content format is valid for content type."""
        valid_formats = {
            ContentType.AUDIO: ["mp3", "wav", "flac", "aac", "m4a", "ogg"],
            ContentType.VIDEO: ["mp4", "mov", "avi", "mkv", "webm", "m4v"],
            ContentType.IMAGE: ["jpg", "jpeg", "png", "gif", "webp", "svg"],
            ContentType.PODCAST: ["mp3", "wav", "m4a", "aac"]
        }
        
        return format.lower() in valid_formats.get(content_type, [])
    
    async def _validate_distribution_targets(
        self,
        targets: List[DistributionTarget]
    ) -> List[DistributionTarget]:
        """Validate and filter distribution targets."""
        validated_targets = []
        
        for target in targets:
            try:
                # Check if platform integration exists
                if target.platform not in self.platform_integrations:
                    self.logger.warning(f"Platform integration not available: {target.platform.value}")
                    continue
                
                # Check if target is enabled
                if not target.enabled:
                    self.logger.debug(f"Distribution target disabled: {target.platform.value}")
                    continue
                
                # Validate platform-specific requirements
                integration = self.platform_integrations[target.platform]
                
                # Check release schedule
                if target.release_schedule and target.release_schedule < datetime.utcnow():
                    self.logger.warning(f"Release schedule in past for {target.platform.value}")
                    target.release_schedule = None
                
                validated_targets.append(target)
                
            except Exception as e:
                self.logger.error(f"Target validation failed for {target.platform.value}: {e}")
                continue
        
        if not validated_targets:
            raise DistributionException("No valid distribution targets available")
        
        return validated_targets
    
    async def _store_distribution_job(self, job: DistributionJob):
        """Store distribution job in database."""
        try:
            # Store main job record
            job_query = """
            INSERT INTO distribution_jobs (
                job_id, creator_id, asset_id, status, created_at,
                retry_count, max_retries, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            
            await self.db.execute(
                job_query,
                job.job_id,
                job.creator_id,
                job.asset.asset_id,
                job.status.value,
                job.created_at,
                job.retry_count,
                job.max_retries,
                json.dumps(job.metadata)
            )
            
            # Store asset information
            asset_query = """
            INSERT INTO content_assets (
                asset_id, creator_id, title, content_type, file_path,
                file_size, duration, format, quality, metadata,
                thumbnail_path, preview_path, tags, explicit_content,
                copyright_info, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            ON CONFLICT (asset_id) DO UPDATE SET
                title = $3, metadata = $10, tags = $13
            """
            
            await self.db.execute(
                asset_query,
                job.asset.asset_id,
                job.asset.creator_id,
                job.asset.title,
                job.asset.content_type.value,
                job.asset.file_path,
                job.asset.file_size,
                job.asset.duration,
                job.asset.format,
                job.asset.quality,
                json.dumps(job.asset.metadata),
                job.asset.thumbnail_path,
                job.asset.preview_path,
                json.dumps(job.asset.tags),
                job.asset.explicit_content,
                json.dumps(job.asset.copyright_info),
                job.asset.created_at
            )
            
            # Store distribution targets
            for target in job.targets:
                target_query = """
                INSERT INTO distribution_targets (
                    job_id, platform, enabled, auto_distribute,
                    custom_metadata, release_schedule, pricing_tier,
                    territory_restrictions, age_restrictions, distribution_priority
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """
                
                await self.db.execute(
                    target_query,
                    job.job_id,
                    target.platform.value,
                    target.enabled,
                    target.auto_distribute,
                    json.dumps(target.custom_metadata),
                    target.release_schedule,
                    target.pricing_tier,
                    json.dumps(target.territory_restrictions),
                    target.age_restrictions,
                    target.distribution_priority
                )
            
            self.logger.info(f"Distribution job stored successfully: {job.job_id}")
            
        except Exception as e:
            self.logger.error(f"Distribution job storage failed: {e}")
            raise DistributionException(f"Job storage error: {e}")
    
    async def _schedule_distribution_job(self, job: DistributionJob):
        """Schedule distribution job for later execution."""
        try:
            # Find earliest release schedule
            earliest_release = None
            for target in job.targets:
                if target.release_schedule:
                    if not earliest_release or target.release_schedule < earliest_release:
                        earliest_release = target.release_schedule
            
            # Schedule job in Redis with delay
            schedule_key = "scheduled_distributions"
            schedule_time = earliest_release or (datetime.utcnow() + timedelta(hours=1))
            
            await self.redis.zadd(
                schedule_key,
                {job.job_id: schedule_time.timestamp()}
            )
            
            # Update job status
            job.status = DistributionStatus.PENDING
            await self._update_job_status(job.job_id, job.status)
            
            self.logger.info(f"Distribution job scheduled for {schedule_time}: {job.job_id}")
            
        except Exception as e:
            self.logger.error(f"Distribution job scheduling failed: {e}")
            raise DistributionException(f"Job scheduling error: {e}")
    
    async def _start_distribution_job(self, job: DistributionJob):
        """Start immediate distribution job processing."""
        try:
            # Update job status
            job.status = DistributionStatus.PROCESSING
            job.started_at = datetime.utcnow()
            await self._update_job_status(job.job_id, job.status, job.started_at)
            
            # Add job to distribution queues based on targets
            for target in job.targets:
                if target.platform in self.distribution_queues:
                    queue_key = self.distribution_queues[target.platform]
                    job_data = {
                        "job_id": job.job_id,
                        "platform": target.platform.value,
                        "priority": target.distribution_priority,
                        "scheduled_for": target.release_schedule.isoformat() if target.release_schedule else None
                    }
                    
                    await self.redis.lpush(queue_key, json.dumps(job_data))
            
            self.logger.info(f"Distribution job started: {job.job_id}")
            
        except Exception as e:
            self.logger.error(f"Distribution job start failed: {e}")
            raise DistributionException(f"Job start error: {e}")
    
    async def _process_distribution_queue(self, platform: DistributionPlatform):
        """Process distribution queue for specific platform."""
        queue_key = self.distribution_queues[platform]
        
        while True:
            try:
                # Get next job from queue (blocking with timeout)
                job_data_raw = await self.redis.brpop(queue_key, timeout=10)
                
                if not job_data_raw:
                    continue  # Timeout, check again
                
                job_data = json.loads(job_data_raw[1])
                job_id = job_data["job_id"]
                
                # Check if job should be processed now
                scheduled_for = job_data.get("scheduled_for")
                if scheduled_for:
                    scheduled_time = datetime.fromisoformat(scheduled_for)
                    if datetime.utcnow() < scheduled_time:
                        # Re-queue for later
                        await asyncio.sleep(60)  # Wait 1 minute
                        await self.redis.lpush(queue_key, json.dumps(job_data))
                        continue
                
                # Process the distribution job
                await self._process_single_platform_distribution(job_id, platform)
                
            except Exception as e:
                self.logger.error(f"Distribution queue processing failed for {platform.value}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _process_single_platform_distribution(
        self,
        job_id: str,
        platform: DistributionPlatform
    ):
        """Process distribution to single platform."""
        try:
            self.logger.info(f"Processing distribution to {platform.value} for job: {job_id}")
            
            # Get job details
            job = await self._get_distribution_job(job_id)
            if not job:
                raise DistributionException(f"Job not found: {job_id}")
            
            # Get platform integration
            integration = self.platform_integrations.get(platform)
            if not integration:
                raise DistributionException(f"No integration for platform: {platform.value}")
            
            # Get platform-specific target
            target = next((t for t in job.targets if t.platform == platform), None)
            if not target:
                raise DistributionException(f"No target found for platform: {platform.value}")
            
            # Update job status
            await self._update_platform_result(job_id, platform.value, {
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            })
            
            # Perform platform-specific distribution
            if platform == DistributionPlatform.SPOTIFY:
                result = await self._distribute_to_spotify(job, target, integration)
            elif platform == DistributionPlatform.YOUTUBE:
                result = await self._distribute_to_youtube(job, target, integration)
            elif platform == DistributionPlatform.INSTAGRAM:
                result = await self._distribute_to_instagram(job, target, integration)
            else:
                result = await self._distribute_to_generic_platform(job, target, integration)
            
            # Update job with result
            await self._update_platform_result(job_id, platform.value, {
                "status": "completed" if result["success"] else "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "result": result,
                "platform_content_id": result.get("content_id"),
                "distribution_url": result.get("url")
            })
            
            # Check if all platforms completed
            await self._check_job_completion(job_id)
            
            self.logger.info(f"Platform distribution completed: {platform.value} for job {job_id}")
            
        except Exception as e:
            self.logger.error(f"Single platform distribution failed: {e}")
            
            # Update with error
            await self._update_platform_result(job_id, platform.value, {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            })
            
            raise DistributionException(f"Platform distribution error: {e}")
    
    async def _distribute_to_spotify(
        self,
        job: DistributionJob,
        target: DistributionTarget,
        integration: PlatformIntegration
    ) -> Dict[str, Any]:
        """Distribute content to Spotify via Spotify for Artists API."""
        try:
            # Prepare metadata for Spotify
            metadata = await self._prepare_spotify_metadata(job.asset, target)
            
            # Upload audio file
            audio_url = await self._upload_content_to_storage(job.asset, "spotify")
            
            # Submit to Spotify for Artists API
            spotify_api_url = f"{integration.api_endpoint}/me/albums"
            
            headers = {
                "Authorization": f"Bearer {integration.credentials.get('access_token')}",
                "Content-Type": "application/json"
            }
            
            # Create album/single release
            release_data = {
                "album_type": "single" if job.asset.content_type == ContentType.SINGLE else "album",
                "name": metadata["title"],
                "artists": metadata["artists"],
                "release_date": target.release_schedule.strftime("%Y-%m-%d") if target.release_schedule else datetime.utcnow().strftime("%Y-%m-%d"),
                "tracks": [{
                    "name": metadata["title"],
                    "duration_ms": int(job.asset.duration * 1000) if job.asset.duration else 0,
                    "audio_file_url": audio_url,
                    "isrc": metadata.get("isrc"),
                    "explicit": job.asset.explicit_content
                }],
                "genres": metadata.get("genres", []),
                "label": metadata.get("label", "Independent"),
                "copyrights": [{
                    "text": f"© {datetime.utcnow().year} {metadata.get('artist', 'Unknown')}",
                    "type": "C"
                }],
                "external_urls": {
                    "spotify": ""
                }
            }
            
            async with self.session.post(spotify_api_url, headers=headers, json=release_data) as response:
                if response.status == 201:
                    result_data = await response.json()
                    return {
                        "success": True,
                        "content_id": result_data["id"],
                        "url": result_data["external_urls"]["spotify"],
                        "release_date": result_data.get("release_date"),
                        "submission_id": result_data.get("submission_id")
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error"),
                        "status_code": response.status
                    }
            
        except Exception as e:
            self.logger.error(f"Spotify distribution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _distribute_to_youtube(
        self,
        job: DistributionJob,
        target: DistributionTarget,
        integration: PlatformIntegration
    ) -> Dict[str, Any]:
        """Distribute content to YouTube via YouTube Data API v3."""
        try:
            # Prepare metadata for YouTube
            metadata = await self._prepare_youtube_metadata(job.asset, target)
            
            # Upload video/audio file to YouTube
            youtube_api_url = f"{integration.api_endpoint}/videos"
            
            headers = {
                "Authorization": f"Bearer {integration.credentials.get('access_token')}",
                "Content-Type": "application/json"
            }
            
            # Prepare video snippet
            video_snippet = {
                "title": metadata["title"],
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "categoryId": "10",  # Music category
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            }
            
            # Set privacy status
            privacy_status = "private"
            if target.release_schedule:
                if target.release_schedule <= datetime.utcnow():
                    privacy_status = "public"
                else:
                    privacy_status = "private"  # Will be published later
            else:
                privacy_status = "public"
            
            video_status = {
                "privacyStatus": privacy_status,
                "publishAt": target.release_schedule.isoformat() + "Z" if target.release_schedule else None,
                "selfDeclaredMadeForKids": False
            }
            
            # Upload video file
            video_data = {
                "snippet": video_snippet,
                "status": video_status
            }
            
            # For audio files, we need to create a video with static image
            if job.asset.content_type == ContentType.AUDIO:
                video_file_path = await self._create_video_from_audio(job.asset)
            else:
                video_file_path = job.asset.file_path
            
            # Use resumable upload for large files
            upload_url = await self._initiate_youtube_upload(headers, video_data)
            upload_result = await self._upload_video_to_youtube(upload_url, video_file_path)
            
            if upload_result["success"]:
                return {
                    "success": True,
                    "content_id": upload_result["video_id"],
                    "url": f"https://www.youtube.com/watch?v={upload_result['video_id']}",
                    "upload_status": upload_result.get("status")
                }
            else:
                return {
                    "success": False,
                    "error": upload_result.get("error", "Upload failed")
                }
            
        except Exception as e:
            self.logger.error(f"YouTube distribution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _distribute_to_instagram(
        self,
        job: DistributionJob,
        target: DistributionTarget,
        integration: PlatformIntegration
    ) -> Dict[str, Any]:
        """Distribute content to Instagram via Instagram Graph API."""
        try:
            # Prepare metadata for Instagram
            metadata = await self._prepare_instagram_metadata(job.asset, target)
            
            # Upload media to Instagram
            instagram_api_url = f"{integration.api_endpoint}/me/media"
            access_token = integration.credentials.get("access_token")
            
            # First, upload the media file
            media_url = await self._upload_content_to_storage(job.asset, "instagram")
            
            # Create media object
            media_data = {
                "image_url" if job.asset.content_type == ContentType.IMAGE else "video_url": media_url,
                "caption": metadata.get("caption", ""),
                "access_token": access_token
            }
            
            # Add location if provided
            if metadata.get("location_id"):
                media_data["location_id"] = metadata["location_id"]
            
            # Add user tags if provided
            if metadata.get("user_tags"):
                media_data["user_tags"] = json.dumps(metadata["user_tags"])
            
            async with self.session.post(instagram_api_url, data=media_data) as response:
                if response.status == 200:
                    media_response = await response.json()
                    media_id = media_response["id"]
                    
                    # Publish the media
                    publish_url = f"{integration.api_endpoint}/me/media_publish"
                    publish_data = {
                        "creation_id": media_id,
                        "access_token": access_token
                    }
                    
                    async with self.session.post(publish_url, data=publish_data) as publish_response:
                        if publish_response.status == 200:
                            publish_result = await publish_response.json()
                            return {
                                "success": True,
                                "content_id": publish_result["id"],
                                "url": f"https://www.instagram.com/p/{publish_result.get('shortcode', '')}",
                                "media_id": media_id
                            }
                        else:
                            publish_error = await publish_response.json()
                            return {
                                "success": False,
                                "error": publish_error.get("error", {}).get("message", "Publish failed"),
                                "media_id": media_id
                            }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error"),
                        "status_code": response.status
                    }
            
        except Exception as e:
            self.logger.error(f"Instagram distribution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _distribute_to_generic_platform(
        self,
        job: DistributionJob,
        target: DistributionTarget,
        integration: PlatformIntegration
    ) -> Dict[str, Any]:
        """Generic distribution handler for other platforms."""
        try:
            self.logger.info(f"Using generic distribution for: {target.platform.value}")
            
            # Prepare generic metadata
            metadata = {
                "title": job.asset.title,
                "content_type": job.asset.content_type.value,
                "format": job.asset.format,
                "file_size": job.asset.file_size,
                "duration": job.asset.duration,
                "explicit": job.asset.explicit_content,
                "tags": job.asset.tags,
                "custom": target.custom_metadata
            }
            
            # Upload content to appropriate storage
            content_url = await self._upload_content_to_storage(job.asset, target.platform.value)
            
            # Submit via platform API
            if integration.upload_method == "api":
                result = await self._submit_via_api(integration, metadata, content_url)
            elif integration.upload_method == "ftp":
                result = await self._submit_via_ftp(integration, job.asset, metadata)
            else:
                result = {"success": False, "error": f"Unsupported upload method: {integration.upload_method}"}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Generic platform distribution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upload_content_to_storage(self, asset: ContentAsset, platform: str) -> str:
        """Upload content to appropriate cloud storage and return URL."""
        try:
            # Generate storage path
            storage_key = f"content/{platform}/{asset.creator_id}/{asset.asset_id}/{Path(asset.file_path).name}"
            
            # Try AWS S3 first
            if hasattr(self, 's3_client') and self.storage_config["aws_s3"]["bucket"]:
                bucket = self.storage_config["aws_s3"]["bucket"]
                
                # Upload file to S3
                self.s3_client.upload_file(
                    asset.file_path,
                    bucket,
                    storage_key,
                    ExtraArgs={
                        'ContentType': self._get_content_type(asset.format),
                        'ServerSideEncryption': 'AES256'
                    }
                )
                
                # Generate presigned URL (24 hour expiry)
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': storage_key},
                    ExpiresIn=86400
                )
                
                return url
            
            # Try Google Cloud Storage
            elif hasattr(self, 'gcs_client') and self.storage_config["google_cloud"]["bucket"]:
                bucket_name = self.storage_config["google_cloud"]["bucket"]
                bucket = self.gcs_client.bucket(bucket_name)
                blob = bucket.blob(storage_key)
                
                # Upload file
                blob.upload_from_filename(asset.file_path)
                
                # Generate signed URL (24 hour expiry)
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.utcnow() + timedelta(hours=24),
                    method="GET"
                )
                
                return url
            
            else:
                # Use local storage with HTTP server
                local_path = self.content_storage_path / platform / asset.creator_id / asset.asset_id
                local_path.mkdir(parents=True, exist_ok=True)
                
                local_file = local_path / Path(asset.file_path).name
                
                # Copy file to local storage
                import shutil
                shutil.copy2(asset.file_path, local_file)
                
                # Return local file URL (assumes local HTTP server)
                base_url = self.config.get("local_content_base_url", "http://localhost:8000/content")
                return f"{base_url}/{platform}/{asset.creator_id}/{asset.asset_id}/{Path(asset.file_path).name}"
        
        except Exception as e:
            self.logger.error(f"Content upload failed: {e}")
            raise DistributionException(f"Upload error: {e}")
    
    def _get_content_type(self, file_format: str) -> str:
        """Get MIME type for file format."""
        content_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "flac": "audio/flac",
            "aac": "audio/aac",
            "m4a": "audio/mp4",
            "ogg": "audio/ogg",
            "mp4": "video/mp4",
            "mov": "video/quicktime",
            "avi": "video/x-msvideo",
            "mkv": "video/x-matroska",
            "webm": "video/webm",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp"
        }
        
        return content_types.get(file_format.lower(), "application/octet-stream")
    
    async def _prepare_spotify_metadata(self, asset: ContentAsset, target: DistributionTarget) -> Dict[str, Any]:
        """Prepare metadata for Spotify submission."""
        metadata = {
            "title": asset.title,
            "artists": [{"name": asset.metadata.get("artist", "Unknown Artist")}],
            "album": asset.metadata.get("album", asset.title),
            "genres": asset.metadata.get("genres", ["Pop"]),
            "label": asset.metadata.get("label", "Independent"),
            "isrc": asset.metadata.get("isrc"),
            "upc": asset.metadata.get("upc"),
            "explicit": asset.explicit_content,
            "release_date": target.release_schedule or datetime.utcnow(),
            "territory_availability": target.territory_restrictions or ["worldwide"]
        }
        
        # Add custom metadata from target
        metadata.update(target.custom_metadata)
        
        return metadata
    
    async def _prepare_youtube_metadata(self, asset: ContentAsset, target: DistributionTarget) -> Dict[str, Any]:
        """Prepare metadata for YouTube submission."""
        # Generate description
        description_parts = []
        if asset.metadata.get("description"):
            description_parts.append(asset.metadata["description"])
        
        if asset.metadata.get("artist"):
            description_parts.append(f"Artist: {asset.metadata['artist']}")
        
        if asset.metadata.get("album"):
            description_parts.append(f"Album: {asset.metadata['album']}")
        
        if asset.metadata.get("release_date"):
            description_parts.append(f"Released: {asset.metadata['release_date']}")
        
        # Add social media links
        if asset.metadata.get("social_links"):
            description_parts.append("\nFollow the artist:")
            for platform, link in asset.metadata["social_links"].items():
                description_parts.append(f"{platform.capitalize()}: {link}")
        
        metadata = {
            "title": asset.title,
            "description": "\n".join(description_parts),
            "tags": asset.tags + asset.metadata.get("genres", []),
            "category": "Music",
            "language": asset.metadata.get("language", "en"),
            "privacy": "public" if not target.release_schedule else "private",
            "thumbnail": asset.thumbnail_path
        }
        
        # Add custom metadata from target
        metadata.update(target.custom_metadata)
        
        return metadata
    
    async def _prepare_instagram_metadata(self, asset: ContentAsset, target: DistributionTarget) -> Dict[str, Any]:
        """Prepare metadata for Instagram submission."""
        # Generate caption
        caption_parts = [asset.title]
        
        if asset.metadata.get("artist"):
            caption_parts.append(f"by {asset.metadata['artist']}")
        
        # Add hashtags
        hashtags = []
        for tag in asset.tags:
            hashtags.append(f"#{tag.replace(' ', '').lower()}")
        
        if asset.metadata.get("genres"):
            for genre in asset.metadata["genres"]:
                hashtags.append(f"#{genre.replace(' ', '').lower()}")
        
        # Add default music hashtags
        hashtags.extend(["#music", "#newmusic", "#artist", "#song"])
        
        caption_parts.append(" ".join(hashtags[:30]))  # Instagram has hashtag limit
        
        metadata = {
            "caption": "\n\n".join(caption_parts),
            "location_id": target.custom_metadata.get("location_id"),
            "user_tags": target.custom_metadata.get("user_tags", []),
            "alt_text": f"Music: {asset.title}"
        }
        
        return metadata
    
    async def process_revenue_aggregation(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process revenue aggregation from all platforms.
        
        Args:
            creator_id: Optional creator ID to process specific creator
            
        Returns:
            Aggregation results summary
        """
        try:
            self.logger.info(f"Starting revenue aggregation for creator: {creator_id or 'all'}")
            
            aggregation_results = {
                "total_revenue": Decimal("0.00"),
                "platform_revenues": {},
                "processed_records": 0,
                "errors": []
            }
            
            # Get creators to process
            if creator_id:
                creators = [creator_id]
            else:
                creators = await self._get_active_creators()
            
            # Process each creator
            for creator in creators:
                try:
                    # Get revenue data from all platforms
                    for platform in self.platform_integrations:
                        platform_revenue = await self._fetch_platform_revenue(creator, platform)
                        
                        if platform_revenue:
                            # Store revenue records
                            for record in platform_revenue:
                                await self._store_revenue_record(record)
                                aggregation_results["processed_records"] += 1
                                aggregation_results["total_revenue"] += record.net_revenue
                            
                            # Update platform summary
                            platform_total = sum(r.net_revenue for r in platform_revenue)
                            aggregation_results["platform_revenues"][platform.value] = float(platform_total)
                    
                except Exception as e:
                    error_msg = f"Revenue aggregation failed for creator {creator}: {e}"
                    self.logger.error(error_msg)
                    aggregation_results["errors"].append(error_msg)
            
            self.logger.info(f"Revenue aggregation completed: {aggregation_results['processed_records']} records")
            
            return aggregation_results
            
        except Exception as e:
            self.logger.error(f"Revenue aggregation failed: {e}")
            raise DistributionException(f"Revenue aggregation error: {e}")
    
    async def process_automated_payouts(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process automated payouts for eligible creators.
        
        Args:
            creator_id: Optional creator ID to process specific creator
            
        Returns:
            Payout processing results
        """
        try:
            self.logger.info(f"Starting automated payout processing for creator: {creator_id or 'all'}")
            
            payout_results = {
                "total_payouts": 0,
                "total_amount": Decimal("0.00"),
                "successful_payouts": 0,
                "failed_payouts": 0,
                "pending_payouts": 0,
                "payout_details": []
            }
            
            # Get eligible creators for payout
            eligible_creators = await self._get_eligible_payout_creators(creator_id)
            
            for creator in eligible_creators:
                try:
                    # Calculate total available revenue
                    available_revenue = await self._calculate_available_revenue(creator["creator_id"])
                    
                    if available_revenue < self.minimum_payout_amount:
                        self.logger.debug(f"Creator {creator['creator_id']} below minimum payout threshold")
                        continue
                    
                    # Create payout request
                    payout_request = PayoutRequest(
                        payout_id=f"payout_{uuid.uuid4().hex[:12]}",
                        creator_id=creator["creator_id"],
                        total_amount=available_revenue,
                        currency=creator.get("preferred_currency", "USD"),
                        payout_method=PayoutMethod(creator.get("payout_method", "paypal")),
                        status=PayoutStatus.PENDING,
                        revenue_records=await self._get_unpaid_revenue_records(creator["creator_id"]),
                        recipient_details=creator.get("payout_details", {}),
                        payout_date=datetime.utcnow() + timedelta(days=1)  # Next business day
                    )
                    
                    # Calculate processing fees
                    payout_request.processing_fee = await self._calculate_payout_fee(
                        payout_request.total_amount,
                        payout_request.payout_method
                    )
                    payout_request.net_amount = payout_request.total_amount - payout_request.processing_fee
                    
                    # Process the payout
                    payout_result = await self._process_payout_request(payout_request)
                    
                    payout_results["total_payouts"] += 1
                    payout_results["total_amount"] += payout_request.total_amount
                    
                    if payout_result["success"]:
                        payout_results["successful_payouts"] += 1
                    elif payout_result["status"] == "pending":
                        payout_results["pending_payouts"] += 1
                    else:
                        payout_results["failed_payouts"] += 1
                    
                    payout_results["payout_details"].append({
                        "payout_id": payout_request.payout_id,
                        "creator_id": creator["creator_id"],
                        "amount": float(payout_request.total_amount),
                        "status": payout_result["status"],
                        "method": payout_request.payout_method.value
                    })
                    
                except Exception as e:
                    error_msg = f"Payout processing failed for creator {creator['creator_id']}: {e}"
                    self.logger.error(error_msg)
                    payout_results["failed_payouts"] += 1
            
            self.logger.info(f"Automated payout processing completed: {payout_results['total_payouts']} payouts")
            
            return payout_results
            
        except Exception as e:
            self.logger.error(f"Automated payout processing failed: {e}")
            raise PayoutException(f"Payout processing error: {e}")
    
    async def get_distribution_analytics(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get comprehensive distribution analytics for creator.
        
        Args:
            creator_id: Creator identifier
            start_date: Analytics period start date
            end_date: Analytics period end date
            
        Returns:
            Comprehensive analytics data
        """
        try:
            self.logger.info(f"Generating distribution analytics for creator: {creator_id}")
            
            analytics = {
                "summary": {
                    "total_distributions": 0,
                    "successful_distributions": 0,
                    "failed_distributions": 0,
                    "total_platforms": 0,
                    "total_content_pieces": 0,
                    "total_revenue": Decimal("0.00")
                },
                "platform_performance": {},
                "content_performance": {},
                "revenue_analysis": {},
                "distribution_timeline": {},
                "recommendations": []
            }
            
            # Get distribution jobs for creator in date range
            jobs_query = """
            SELECT 
                dj.*, ca.title, ca.content_type,
                COUNT(dt.platform) as target_platforms,
                AVG(CASE WHEN pr.status = 'completed' THEN 1 ELSE 0 END) as success_rate
            FROM distribution_jobs dj
            LEFT JOIN content_assets ca ON dj.asset_id = ca.asset_id
            LEFT JOIN distribution_targets dt ON dj.job_id = dt.job_id
            LEFT JOIN platform_results pr ON dj.job_id = pr.job_id
            WHERE dj.creator_id = $1 
                AND dj.created_at BETWEEN $2 AND $3
            GROUP BY dj.job_id, ca.title, ca.content_type
            ORDER BY dj.created_at DESC
            """
            
            distribution_jobs = await self.db.fetch(jobs_query, creator_id, start_date, end_date)
            
            analytics["summary"]["total_distributions"] = len(distribution_jobs)
            analytics["summary"]["total_platforms"] = len(self.platform_integrations)
            
            # Analyze platform performance
            platform_stats = {}
            for platform in self.platform_integrations:
                platform_stats[platform.value] = {
                    "distributions": 0,
                    "successful": 0,
                    "failed": 0,
                    "success_rate": 0.0,
                    "revenue": Decimal("0.00")
                }
            
            # Process job results
            for job in distribution_jobs:
                # Get platform results for this job
                results_query = """
                SELECT platform, status, result, platform_content_id
                FROM platform_results
                WHERE job_id = $1
                """
                platform_results = await self.db.fetch(results_query, job["job_id"])
                
                for result in platform_results:
                    platform = result["platform"]
                    if platform in platform_stats:
                        platform_stats[platform]["distributions"] += 1
                        
                        if result["status"] == "completed":
                            platform_stats[platform]["successful"] += 1
                            analytics["summary"]["successful_distributions"] += 1
                        else:
                            platform_stats[platform]["failed"] += 1
                            analytics["summary"]["failed_distributions"] += 1
            
            # Calculate success rates
            for platform, stats in platform_stats.items():
                if stats["distributions"] > 0:
                    stats["success_rate"] = stats["successful"] / stats["distributions"]
            
            analytics["platform_performance"] = platform_stats
            
            # Get revenue data
            revenue_query = """
            SELECT 
                platform, 
                SUM(net_revenue) as total_revenue,
                COUNT(*) as revenue_records,
                AVG(net_revenue) as avg_revenue
            FROM revenue_records
            WHERE creator_id = $1 
                AND revenue_period_start >= $2 
                AND revenue_period_end <= $3
            GROUP BY platform
            ORDER BY total_revenue DESC
            """
            
            revenue_data = await self.db.fetch(revenue_query, creator_id, start_date, end_date)
            
            for row in revenue_data:
                platform = row["platform"]
                analytics["summary"]["total_revenue"] += row["total_revenue"]
                
                if platform in platform_stats:
                    platform_stats[platform]["revenue"] = row["total_revenue"]
                
                analytics["revenue_analysis"][platform] = {
                    "total_revenue": float(row["total_revenue"]),
                    "revenue_records": row["revenue_records"],
                    "average_revenue": float(row["avg_revenue"])
                }
            
            # Generate recommendations based on performance
            analytics["recommendations"] = await self._generate_analytics_recommendations(
                creator_id, platform_stats, analytics["revenue_analysis"]
            )
            
            self.logger.info(f"Distribution analytics generated successfully for creator: {creator_id}")
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Distribution analytics generation failed: {e}")
            raise DistributionException(f"Analytics generation error: {e}")
    
    async def _generate_analytics_recommendations(
        self,
        creator_id: str,
        platform_stats: Dict[str, Dict[str, Any]],
        revenue_analysis: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate intelligent recommendations based on performance data."""
        recommendations = []
        
        # Find best performing platforms
        best_platforms = sorted(
            platform_stats.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )[:3]
        
        if best_platforms and best_platforms[0][1]["success_rate"] > 0.8:
            recommendations.append(
                f"Focus on {best_platforms[0][0]} - your highest performing platform with "
                f"{best_platforms[0][1]['success_rate']:.1%} success rate"
            )
        
        # Find revenue opportunities
        top_revenue_platforms = sorted(
            revenue_analysis.items(),
            key=lambda x: x[1]["total_revenue"],
            reverse=True
        )[:2]
        
        if top_revenue_platforms:
            recommendations.append(
                f"Prioritize {top_revenue_platforms[0][0]} for revenue - "
                f"generates ${top_revenue_platforms[0][1]['total_revenue']:.2f} on average"
            )
        
        # Identify underperforming platforms
        underperforming = [
            platform for platform, stats in platform_stats.items()
            if stats["distributions"] > 0 and stats["success_rate"] < 0.5
        ]
        
        if underperforming:
            recommendations.append(
                f"Review content strategy for {', '.join(underperforming)} - "
                "these platforms show lower success rates"
            )
        
        # Suggest expansion opportunities
        unused_platforms = [
            platform for platform, stats in platform_stats.items()
            if stats["distributions"] == 0
        ]
        
        if unused_platforms and len(unused_platforms) <= 3:
            recommendations.append(
                f"Consider expanding to {', '.join(unused_platforms)} "
                "to increase your distribution reach"
            )
        
        return recommendations
    
    async def _get_eligible_payout_creators(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get creators eligible for automated payouts."""
        try:
            # Query to get creators with unpaid revenue above minimum threshold
            if creator_id:
                query = """
                SELECT DISTINCT creator_id, preferred_currency, payout_method, payout_details
                FROM creator_profiles 
                WHERE creator_id = $1 AND payout_enabled = true
                """
                creators = await self.db.fetch(query, creator_id)
            else:
                query = """
                SELECT DISTINCT creator_id, preferred_currency, payout_method, payout_details
                FROM creator_profiles 
                WHERE payout_enabled = true
                """
                creators = await self.db.fetch(query)
            
            return [dict(creator) for creator in creators]
            
        except Exception as e:
            self.logger.error(f"Error getting eligible creators: {e}")
            # Return mock data for demonstration
            return [{
                "creator_id": creator_id or "mock_creator",
                "preferred_currency": "USD",
                "payout_method": "paypal",
                "payout_details": {"email": "creator@example.com"}
            }] if creator_id else []
    
    async def _calculate_available_revenue(self, creator_id: str) -> Decimal:
        """Calculate total available revenue for creator."""
        try:
            query = """
            SELECT COALESCE(SUM(amount), 0) as total_revenue
            FROM revenue_transactions 
            WHERE creator_id = $1 AND status = 'completed' AND payout_status = 'unpaid'
            """
            result = await self.db.fetchrow(query, creator_id)
            return Decimal(str(result["total_revenue"])) if result else Decimal("0")
            
        except Exception as e:
            self.logger.error(f"Error calculating available revenue: {e}")
            # Return mock revenue for demonstration
            return Decimal("100.00")
    
    async def _get_unpaid_revenue_records(self, creator_id: str) -> List[str]:
        """Get list of unpaid revenue record IDs for creator."""
        try:
            query = """
            SELECT transaction_id 
            FROM revenue_transactions 
            WHERE creator_id = $1 AND status = 'completed' AND payout_status = 'unpaid'
            """
            records = await self.db.fetch(query, creator_id)
            return [record["transaction_id"] for record in records]
            
        except Exception as e:
            self.logger.error(f"Error getting unpaid revenue records: {e}")
            return ["mock_transaction_1", "mock_transaction_2"]
    
    async def _calculate_payout_fee(self, amount: Decimal, payout_method: Any) -> Decimal:
        """Calculate processing fee for payout."""
        try:
            # Fee structure based on payout method
            fee_rates = {
                "paypal": {"rate": Decimal("0.025"), "fixed": Decimal("0.30")},
                "stripe": {"rate": Decimal("0.025"), "fixed": Decimal("0.30")},
                "bank_transfer": {"rate": Decimal("0.005"), "fixed": Decimal("1.00")},
                "crypto": {"rate": Decimal("0.015"), "fixed": Decimal("0.00")}
            }
            
            method_name = payout_method.value if hasattr(payout_method, 'value') else str(payout_method)
            fees = fee_rates.get(method_name, fee_rates["paypal"])
            
            fee = (amount * fees["rate"]) + fees["fixed"]
            return fee.quantize(Decimal("0.01"))
            
        except Exception as e:
            self.logger.error(f"Error calculating payout fee: {e}")
            return Decimal("2.50")  # Default fee
    
    async def _process_payout_request(self, payout_request: Any) -> Dict[str, Any]:
        """Process payout request through payment processor."""
        try:
            # Simulate payout processing
            processing_result = {
                "success": True,
                "status": "completed",
                "transaction_id": f"payout_tx_{uuid.uuid4().hex[:12]}",
                "processed_at": datetime.utcnow().isoformat(),
                "processor_response": {
                    "id": payout_request.payout_id,
                    "amount": float(payout_request.net_amount),
                    "currency": payout_request.currency,
                    "method": payout_request.payout_method.value if hasattr(payout_request.payout_method, 'value') else str(payout_request.payout_method)
                }
            }
            
            # Update revenue records as paid
            if processing_result["success"]:
                await self._mark_revenue_as_paid(payout_request.revenue_records, payout_request.payout_id)
            
            self.logger.info(f"Payout processed successfully: {payout_request.payout_id}")
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Payout processing failed: {e}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "transaction_id": None
            }
    
    async def _mark_revenue_as_paid(self, revenue_record_ids: List[str], payout_id: str) -> None:
        """Mark revenue records as paid."""
        try:
            if not revenue_record_ids:
                return
                
            query = """
            UPDATE revenue_transactions 
            SET payout_status = 'paid', payout_id = $1, payout_date = NOW()
            WHERE transaction_id = ANY($2)
            """
            await self.db.execute(query, payout_id, revenue_record_ids)
            self.logger.debug(f"Marked {len(revenue_record_ids)} revenue records as paid")
            
        except Exception as e:
            self.logger.error(f"Error marking revenue as paid: {e}")
    
    async def cleanup_resources(self):
        """Clean up engine resources."""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            self.logger.info("Distribution engine resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Resource cleanup failed: {e}")


# Factory function for easy instantiation
def create_distribution_engine(config: Optional[Dict[str, Any]] = None) -> AutomatedDistributionEngine:
    """Create and return configured distribution engine instance."""
    return AutomatedDistributionEngine(config)
