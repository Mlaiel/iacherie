#!/usr/bin/env python3
"""🌐 Distribution Orchestrator - Multi-Platform Content Distribution Platform
================================================================
Expert: PLATFORM ARCHITECT + BACKEND SENIOR + CREATOR ECONOMY SPECIALIST + DEVOPS EXPERT
Technologies: Multi-Platform Distribution + Content Syndication + Automated Publishing + Analytics Tracking
Architecture: Level 3 - Distribution Intelligence Layer
Date: 2025-01-25

Ultra-advanced content distribution orchestration across multiple platforms with
intelligent scheduling, format optimization, audience targeting and performance tracking.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import statistics
from collections import defaultdict, deque
import hashlib
import base64

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Plateformes de distribution supportées"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    REDDIT = "reddit"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CLUBHOUSE = "clubhouse"
    PODCAST_PLATFORMS = "podcast_platforms"

class ContentFormat(Enum):
    """Formats de contenu"""
    VIDEO_LONG = "video_long"        # YouTube, Facebook
    VIDEO_SHORT = "video_short"      # TikTok, Instagram Reels, YouTube Shorts
    VIDEO_LIVE = "video_live"        # Twitch, YouTube Live, Instagram Live
    IMAGE_SINGLE = "image_single"    # Instagram Post, Pinterest Pin
    IMAGE_CAROUSEL = "image_carousel" # Instagram Carousel, LinkedIn Carousel
    IMAGE_STORY = "image_story"      # Instagram/Facebook Stories
    TEXT_POST = "text_post"          # Twitter, LinkedIn, Facebook
    TEXT_ARTICLE = "text_article"    # Medium, LinkedIn Articles, Substack
    AUDIO_PODCAST = "audio_podcast"  # Spotify, Apple Podcasts
    AUDIO_LIVE = "audio_live"        # Clubhouse, Twitter Spaces
    INTERACTIVE = "interactive"      # Polls, Q&A, Live Chat

class DistributionStatus(Enum):
    """Statuts de distribution"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    REMOVED = "removed"
    PROCESSING = "processing"

class AudienceSegment(Enum):
    """Segments d'audience"""
    TEENS = "teens"              # 13-17
    YOUNG_ADULTS = "young_adults" # 18-24
    MILLENNIALS = "millennials"   # 25-40
    GEN_X = "gen_x"              # 41-56
    BOOMERS = "boomers"          # 57+
    CREATORS = "creators"
    ENTREPRENEURS = "entrepreneurs"
    STUDENTS = "students"
    PROFESSIONALS = "professionals"
    ARTISTS = "artists"

@dataclass
class PlatformConfig:
    """Configuration de plateforme"""
    platform: Platform
    api_credentials: Dict[str, str]
    content_guidelines: Dict[str, Any]
    supported_formats: List[ContentFormat]
    max_file_size: int  # bytes
    max_duration: int   # seconds for video/audio
    posting_limits: Dict[str, int]  # daily, hourly limits
    optimal_times: List[str]  # ["09:00", "15:00", "20:00"]
    hashtag_limits: Dict[str, int]
    audience_demographics: Dict[str, float]
    is_active: bool = True
    
@dataclass
class ContentAsset:
    """Asset de contenu"""
    asset_id: str
    content_id: str
    format_type: ContentFormat
    file_path: str
    file_size: int
    duration: Optional[int] = None  # for video/audio
    dimensions: Optional[Tuple[int, int]] = None  # for images/video
    thumbnail_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DistributionJob:
    """Job de distribution"""
    job_id: str
    content_id: str
    creator_id: str
    platform: Platform
    content_asset: ContentAsset
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]
    target_audience: List[AudienceSegment]
    scheduled_time: datetime
    status: DistributionStatus
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None

@dataclass
class DistributionCampaign:
    """Campagne de distribution"""
    campaign_id: str
    creator_id: str
    name: str
    content_items: List[str]  # content_ids
    target_platforms: List[Platform]
    start_date: datetime
    end_date: datetime
    budget: float
    goals: Dict[str, float]  # views, engagement, conversions
    audience_targeting: Dict[str, Any]
    distribution_schedule: Dict[Platform, List[datetime]]
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)

class PlatformAPI(ABC):
    """Interface pour les APIs de plateformes"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authentifier avec la plateforme"""
        pass
    
    @abstractmethod
    async def upload_content(self, asset: ContentAsset, metadata: Dict[str, Any]) -> str:
        """Uploader le contenu"""
        pass
    
    @abstractmethod
    async def publish_content(self, content_id: str, publish_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publier le contenu"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self, post_id: str) -> Dict[str, Any]:
        """Obtenir les métriques de performance"""
        pass
    
    @abstractmethod
    async def delete_content(self, post_id: str) -> bool:
        """Supprimer le contenu"""
        pass

class YouTubeAPI(PlatformAPI):
    """API YouTube"""
    
    def __init__(self):
        self.authenticated = False
        self.channel_id = None
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authentifier avec YouTube"""
        try:
            # Simulate YouTube OAuth authentication
            api_key = credentials.get("api_key")
            oauth_token = credentials.get("oauth_token")
            
            if api_key and oauth_token:
                self.authenticated = True
                self.channel_id = f"UC{hash(api_key) % 1000000}"
                logger.info("YouTube API authenticated successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def upload_content(self, asset: ContentAsset, metadata: Dict[str, Any]) -> str:
        """Uploader une vidéo sur YouTube"""
        try:
            if not self.authenticated:
                raise Exception("Not authenticated")
            
            # Simulate video upload
            video_id = f"vid_{uuid.uuid4().hex[:11]}"
            
            # Simulate upload process
            await asyncio.sleep(2)  # Simulate upload time
            
            logger.info(f"Video uploaded to YouTube: {video_id}")
            return video_id
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            raise
    
    async def publish_content(self, content_id: str, publish_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publier une vidéo sur YouTube"""
        try:
            # Simulate publishing
            result = {
                "platform_post_id": content_id,
                "platform_url": f"https://youtube.com/watch?v={content_id}",
                "status": "published",
                "published_at": datetime.now().isoformat()
            }
            
            logger.info(f"Content published on YouTube: {content_id}")
            return result
        except Exception as e:
            logger.error(f"YouTube publish failed: {e}")
            raise
    
    async def get_performance_metrics(self, post_id: str) -> Dict[str, Any]:
        """Obtenir les métriques YouTube"""
        try:
            # Simulate metrics
            metrics = {
                "views": hash(post_id) % 100000 + 1000,
                "likes": hash(post_id) % 5000 + 100,
                "dislikes": hash(post_id) % 500 + 10,
                "comments": hash(post_id) % 1000 + 50,
                "shares": hash(post_id) % 500 + 20,
                "watch_time_minutes": hash(post_id) % 50000 + 5000,
                "subscribers_gained": hash(post_id) % 100 + 10,
                "revenue": round((hash(post_id) % 1000) / 100, 2)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"YouTube metrics failed: {e}")
            return {}
    
    async def delete_content(self, post_id: str) -> bool:
        """Supprimer une vidéo YouTube"""
        try:
            # Simulate deletion
            logger.info(f"YouTube video deleted: {post_id}")
            return True
        except Exception as e:
            logger.error(f"YouTube deletion failed: {e}")
            return False

class InstagramAPI(PlatformAPI):
    """API Instagram"""
    
    def __init__(self):
        self.authenticated = False
        self.user_id = None
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authentifier avec Instagram"""
        try:
            access_token = credentials.get("access_token")
            
            if access_token:
                self.authenticated = True
                self.user_id = f"ig_{hash(access_token) % 1000000}"
                logger.info("Instagram API authenticated successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def upload_content(self, asset: ContentAsset, metadata: Dict[str, Any]) -> str:
        """Uploader du contenu sur Instagram"""
        try:
            if not self.authenticated:
                raise Exception("Not authenticated")
            
            media_id = f"ig_{uuid.uuid4().hex[:11]}"
            
            # Simulate upload
            await asyncio.sleep(1)
            
            logger.info(f"Content uploaded to Instagram: {media_id}")
            return media_id
        except Exception as e:
            logger.error(f"Instagram upload failed: {e}")
            raise
    
    async def publish_content(self, content_id: str, publish_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publier sur Instagram"""
        try:
            result = {
                "platform_post_id": content_id,
                "platform_url": f"https://instagram.com/p/{content_id}",
                "status": "published",
                "published_at": datetime.now().isoformat()
            }
            
            logger.info(f"Content published on Instagram: {content_id}")
            return result
        except Exception as e:
            logger.error(f"Instagram publish failed: {e}")
            raise
    
    async def get_performance_metrics(self, post_id: str) -> Dict[str, Any]:
        """Obtenir les métriques Instagram"""
        try:
            metrics = {
                "likes": hash(post_id) % 10000 + 500,
                "comments": hash(post_id) % 1000 + 50,
                "shares": hash(post_id) % 500 + 25,
                "saves": hash(post_id) % 800 + 40,
                "reach": hash(post_id) % 50000 + 5000,
                "impressions": hash(post_id) % 80000 + 8000,
                "profile_visits": hash(post_id) % 1000 + 100,
                "follows": hash(post_id) % 50 + 5
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Instagram metrics failed: {e}")
            return {}
    
    async def delete_content(self, post_id: str) -> bool:
        """Supprimer un post Instagram"""
        try:
            logger.info(f"Instagram post deleted: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Instagram deletion failed: {e}")
            return False

class ContentFormatter:
    """Formateur de contenu pour différentes plateformes"""
    
    def __init__(self):
        self.platform_requirements = {
            Platform.YOUTUBE: {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 30,
                "hashtags_in_description": True
            },
            Platform.INSTAGRAM: {
                "caption_max_length": 2200,
                "hashtags_max_count": 30,
                "hashtags_in_caption": True
            },
            Platform.TWITTER: {
                "text_max_length": 280,
                "hashtags_max_count": 10,
                "hashtags_in_text": True
            },
            Platform.TIKTOK: {
                "caption_max_length": 150,
                "hashtags_max_count": 20,
                "hashtags_in_caption": True
            },
            Platform.LINKEDIN: {
                "text_max_length": 3000,
                "hashtags_max_count": 10,
                "hashtags_at_end": True
            }
        }
    
    async def format_content_for_platform(
        self, 
        platform: Platform, 
        title: str, 
        description: str, 
        hashtags: List[str]
    ) -> Dict[str, str]:
        """Formater le contenu pour une plateforme spécifique"""
        try:
            requirements = self.platform_requirements.get(platform, {})
            formatted = {}
            
            if platform == Platform.YOUTUBE:
                formatted = await self._format_youtube_content(title, description, hashtags, requirements)
            elif platform == Platform.INSTAGRAM:
                formatted = await self._format_instagram_content(title, description, hashtags, requirements)
            elif platform == Platform.TWITTER:
                formatted = await self._format_twitter_content(title, description, hashtags, requirements)
            elif platform == Platform.TIKTOK:
                formatted = await self._format_tiktok_content(title, description, hashtags, requirements)
            elif platform == Platform.LINKEDIN:
                formatted = await self._format_linkedin_content(title, description, hashtags, requirements)
            else:
                # Default formatting
                formatted = {
                    "title": title[:100],
                    "description": description[:1000],
                    "hashtags": hashtags[:10]
                }
            
            logger.info(f"Content formatted for {platform.value}")
            return formatted
            
        except Exception as e:
            logger.error(f"Content formatting failed for {platform.value}: {e}")
            return {"title": title, "description": description, "hashtags": hashtags}
    
    async def _format_youtube_content(self, title: str, description: str, hashtags: List[str], req: Dict) -> Dict[str, str]:
        """Formater pour YouTube"""
        # YouTube specific formatting
        formatted_title = title[:req["title_max_length"]]
        
        # Add hashtags to description
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:req["tags_max_count"]]])
        formatted_description = f"{description}\n\n{hashtag_text}"
        formatted_description = formatted_description[:req["description_max_length"]]
        
        return {
            "title": formatted_title,
            "description": formatted_description,
            "tags": hashtags[:req["tags_max_count"]]
        }
    
    async def _format_instagram_content(self, title: str, description: str, hashtags: List[str], req: Dict) -> Dict[str, str]:
        """Formater pour Instagram"""
        # Combine title and description
        full_caption = f"{title}\n\n{description}"
        
        # Add hashtags
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:req["hashtags_max_count"]]])
        full_caption = f"{full_caption}\n\n{hashtag_text}"
        
        return {
            "caption": full_caption[:req["caption_max_length"]],
            "hashtags": hashtags[:req["hashtags_max_count"]]
        }
    
    async def _format_twitter_content(self, title: str, description: str, hashtags: List[str], req: Dict) -> Dict[str, str]:
        """Formater pour Twitter"""
        # Combine title and short description
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:req["hashtags_max_count"]]])
        
        available_length = req["text_max_length"] - len(hashtag_text) - 3  # 3 for spacing
        
        if len(title) <= available_length:
            text = f"{title} {hashtag_text}"
        else:
            truncated_title = title[:available_length-3] + "..."
            text = f"{truncated_title} {hashtag_text}"
        
        return {
            "text": text,
            "hashtags": hashtags[:req["hashtags_max_count"]]
        }
    
    async def _format_tiktok_content(self, title: str, description: str, hashtags: List[str], req: Dict) -> Dict[str, str]:
        """Formater pour TikTok"""
        # Short, catchy caption
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:req["hashtags_max_count"]]])
        
        # Use title as main text, add hashtags
        available_length = req["caption_max_length"] - len(hashtag_text) - 2
        
        if len(title) <= available_length:
            caption = f"{title} {hashtag_text}"
        else:
            caption = f"{title[:available_length-3]}... {hashtag_text}"
        
        return {
            "caption": caption,
            "hashtags": hashtags[:req["hashtags_max_count"]]
        }
    
    async def _format_linkedin_content(self, title: str, description: str, hashtags: List[str], req: Dict) -> Dict[str, str]:
        """Formater pour LinkedIn"""
        # Professional formatting
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:req["hashtags_max_count"]]])
        
        full_text = f"{title}\n\n{description}\n\n{hashtag_text}"
        
        return {
            "text": full_text[:req["text_max_length"]],
            "hashtags": hashtags[:req["hashtags_max_count"]]
        }

class DistributionScheduler:
    """Planificateur de distribution intelligent"""
    
    def __init__(self):
        self.optimal_times = {
            Platform.YOUTUBE: ["09:00", "15:00", "20:00"],
            Platform.INSTAGRAM: ["08:00", "12:00", "17:00", "19:00"],
            Platform.TWITTER: ["09:00", "12:00", "15:00", "18:00"],
            Platform.TIKTOK: ["06:00", "10:00", "16:00", "20:00"],
            Platform.LINKEDIN: ["08:00", "12:00", "17:00"],
            Platform.FACEBOOK: ["09:00", "13:00", "15:00"]
        }
        
        self.audience_activity = {
            AudienceSegment.TEENS: ["16:00", "20:00", "22:00"],
            AudienceSegment.YOUNG_ADULTS: ["08:00", "12:00", "19:00"],
            AudienceSegment.PROFESSIONALS: ["07:00", "12:00", "18:00"],
            AudienceSegment.ENTREPRENEURS: ["06:00", "12:00", "21:00"]
        }
    
    async def calculate_optimal_schedule(
        self, 
        platforms: List[Platform], 
        target_audience: List[AudienceSegment],
        start_date: datetime,
        spacing_hours: int = 2
    ) -> Dict[Platform, List[datetime]]:
        """Calculer le planning optimal de distribution"""
        try:
            schedule = {}
            current_time = start_date
            
            for platform in platforms:
                platform_times = []
                platform_optimal = self.optimal_times.get(platform, ["12:00"])
                
                # Get audience-specific times
                audience_times = []
                for segment in target_audience:
                    audience_times.extend(self.audience_activity.get(segment, []))
                
                # Combine platform and audience optimal times
                combined_times = list(set(platform_optimal + audience_times))
                combined_times.sort()
                
                # Generate schedule for next 7 days
                for day in range(7):
                    schedule_date = current_time + timedelta(days=day)
                    
                    for time_str in combined_times:
                        hour, minute = map(int, time_str.split(':'))
                        scheduled_datetime = schedule_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # Only schedule future times
                        if scheduled_datetime > datetime.now():
                            platform_times.append(scheduled_datetime)
                
                # Sort and limit to reasonable number of posts
                platform_times.sort()
                schedule[platform] = platform_times[:10]  # Limit to 10 scheduled posts
            
            # Ensure spacing between platforms
            schedule = await self._apply_spacing_rules(schedule, spacing_hours)
            
            logger.info(f"Optimal schedule calculated for {len(platforms)} platforms")
            return schedule
            
        except Exception as e:
            logger.error(f"Error calculating optimal schedule: {e}")
            return {}
    
    async def _apply_spacing_rules(self, schedule: Dict[Platform, List[datetime]], spacing_hours: int) -> Dict[Platform, List[datetime]]:
        """Appliquer les règles d'espacement entre plateformes"""
        try:
            # Create a list of all scheduled posts with platform info
            all_posts = []
            for platform, times in schedule.items():
                for time in times:
                    all_posts.append((time, platform))
            
            # Sort by time
            all_posts.sort(key=lambda x: x[0])
            
            # Apply spacing rules
            adjusted_schedule = {platform: [] for platform in schedule.keys()}
            last_post_time = None
            
            for post_time, platform in all_posts:
                if last_post_time is None or (post_time - last_post_time).total_seconds() >= spacing_hours * 3600:
                    adjusted_schedule[platform].append(post_time)
                    last_post_time = post_time
                else:
                    # Reschedule to next available slot
                    next_slot = last_post_time + timedelta(hours=spacing_hours)
                    adjusted_schedule[platform].append(next_slot)
                    last_post_time = next_slot
            
            return adjusted_schedule
            
        except Exception as e:
            logger.error(f"Error applying spacing rules: {e}")
            return schedule

class DistributionOrchestrator:
    """🌐 Orchestrateur de Distribution Multi-Plateformes pour Creators"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.platform_configs: Dict[Platform, PlatformConfig] = {}
        self.platform_apis: Dict[Platform, PlatformAPI] = {}
        self.distribution_jobs: Dict[str, DistributionJob] = {}
        self.distribution_campaigns: Dict[str, DistributionCampaign] = {}
        self.content_formatter = ContentFormatter()
        self.scheduler = DistributionScheduler()
        self.job_queue: deque = deque()
        self.processing_jobs: Set[str] = set()
        
        # Initialize platform APIs
        self.platform_apis[Platform.YOUTUBE] = YouTubeAPI()
        self.platform_apis[Platform.INSTAGRAM] = InstagramAPI()
        
        logger.info("🌐 Distribution Orchestrator initialized")
    
    async def configure_platform(
        self, 
        platform: Platform, 
        api_credentials: Dict[str, str],
        content_guidelines: Dict[str, Any] = None,
        posting_limits: Dict[str, int] = None
    ) -> bool:
        """Configurer une plateforme de distribution"""
        try:
            # Authenticate with platform
            platform_api = self.platform_apis.get(platform)
            if platform_api:
                auth_success = await platform_api.authenticate(api_credentials)
                if not auth_success:
                    logger.error(f"Authentication failed for {platform.value}")
                    return False
            
            # Default configurations
            default_guidelines = {
                "max_title_length": 100,
                "max_description_length": 1000,
                "allowed_formats": ["video", "image", "text"],
                "content_policy": "family_friendly"
            }
            
            default_limits = {
                "daily_posts": 10,
                "hourly_posts": 3,
                "weekly_posts": 50
            }
            
            # Create platform configuration
            config = PlatformConfig(
                platform=platform,
                api_credentials=api_credentials,
                content_guidelines=content_guidelines or default_guidelines,
                supported_formats=[ContentFormat.VIDEO_LONG, ContentFormat.IMAGE_SINGLE, ContentFormat.TEXT_POST],
                max_file_size=100 * 1024 * 1024,  # 100MB default
                max_duration=3600,  # 1 hour default
                posting_limits=posting_limits or default_limits,
                optimal_times=["09:00", "15:00", "20:00"],
                hashtag_limits={"max_hashtags": 30},
                audience_demographics={"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1}
            )
            
            self.platform_configs[platform] = config
            
            # Store in Redis
            await self.redis_client.hset(
                f"distribution:platform:{platform.value}",
                mapping={
                    "configured": "true",
                    "max_file_size": str(config.max_file_size),
                    "posting_limits": json.dumps(config.posting_limits),
                    "configured_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Platform {platform.value} configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring platform {platform.value}: {e}")
            return False
    
    async def create_distribution_job(
        self,
        content_id: str,
        creator_id: str,
        platform: Platform,
        content_asset: ContentAsset,
        title: str,
        description: str,
        tags: List[str] = None,
        hashtags: List[str] = None,
        target_audience: List[AudienceSegment] = None,
        scheduled_time: datetime = None
    ) -> Optional[DistributionJob]:
        """Créer un job de distribution"""
        try:
            if platform not in self.platform_configs:
                logger.error(f"Platform {platform.value} not configured")
                return None
            
            job_id = str(uuid.uuid4())
            
            # Format content for platform
            formatted_content = await self.content_formatter.format_content_for_platform(
                platform, title, description, hashtags or []
            )
            
            # Create distribution job
            job = DistributionJob(
                job_id=job_id,
                content_id=content_id,
                creator_id=creator_id,
                platform=platform,
                content_asset=content_asset,
                title=formatted_content.get("title", title),
                description=formatted_content.get("description", description),
                tags=tags or [],
                hashtags=hashtags or [],
                target_audience=target_audience or [],
                scheduled_time=scheduled_time or datetime.now(),
                status=DistributionStatus.DRAFT if scheduled_time else DistributionStatus.SCHEDULED
            )
            
            self.distribution_jobs[job_id] = job
            
            # Add to queue if immediate or scheduled for near future
            if not scheduled_time or scheduled_time <= datetime.now() + timedelta(minutes=5):
                self.job_queue.append(job_id)
                job.status = DistributionStatus.SCHEDULED
            
            # Store in Redis
            await self.redis_client.hset(
                f"distribution:job:{job_id}",
                mapping={
                    "content_id": content_id,
                    "creator_id": creator_id,
                    "platform": platform.value,
                    "title": job.title,
                    "status": job.status.value,
                    "scheduled_time": job.scheduled_time.isoformat(),
                    "created_at": job.created_at.isoformat()
                }
            )
            
            logger.info(f"Distribution job created: {job_id} for {platform.value}")
            return job
            
        except Exception as e:
            logger.error(f"Error creating distribution job: {e}")
            return None
    
    async def create_distribution_campaign(
        self,
        creator_id: str,
        name: str,
        content_items: List[str],
        target_platforms: List[Platform],
        start_date: datetime,
        end_date: datetime,
        target_audience: List[AudienceSegment] = None,
        budget: float = 0.0
    ) -> Optional[DistributionCampaign]:
        """Créer une campagne de distribution"""
        try:
            campaign_id = str(uuid.uuid4())
            
            # Calculate optimal distribution schedule
            distribution_schedule = await self.scheduler.calculate_optimal_schedule(
                target_platforms, target_audience or [], start_date
            )
            
            # Create campaign
            campaign = DistributionCampaign(
                campaign_id=campaign_id,
                creator_id=creator_id,
                name=name,
                content_items=content_items,
                target_platforms=target_platforms,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                goals={"total_reach": 100000, "engagement_rate": 5.0},
                audience_targeting={"segments": [seg.value for seg in (target_audience or [])]},
                distribution_schedule=distribution_schedule
            )
            
            self.distribution_campaigns[campaign_id] = campaign
            
            # Store in Redis
            await self.redis_client.hset(
                f"distribution:campaign:{campaign_id}",
                mapping={
                    "creator_id": creator_id,
                    "name": name,
                    "content_count": str(len(content_items)),
                    "platforms": json.dumps([p.value for p in target_platforms]),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "budget": str(budget),
                    "status": campaign.status
                }
            )
            
            logger.info(f"Distribution campaign created: {campaign_id} with {len(content_items)} content items")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating distribution campaign: {e}")
            return None
    
    async def execute_distribution_job(self, job_id: str) -> bool:
        """Exécuter un job de distribution"""
        try:
            if job_id not in self.distribution_jobs:
                logger.error(f"Distribution job {job_id} not found")
                return False
            
            job = self.distribution_jobs[job_id]
            
            # Check if job is ready to execute
            if job.scheduled_time > datetime.now():
                logger.info(f"Job {job_id} scheduled for future execution")
                return False
            
            # Mark as processing
            job.status = DistributionStatus.PROCESSING
            self.processing_jobs.add(job_id)
            
            try:
                # Get platform API
                platform_api = self.platform_apis.get(job.platform)
                if not platform_api:
                    raise Exception(f"Platform API not available for {job.platform.value}")
                
                # Upload content
                job.status = DistributionStatus.PUBLISHING
                upload_result = await platform_api.upload_content(
                    job.content_asset,
                    {
                        "title": job.title,
                        "description": job.description,
                        "tags": job.tags,
                        "hashtags": job.hashtags
                    }
                )
                
                # Publish content
                publish_data = {
                    "title": job.title,
                    "description": job.description,
                    "tags": job.tags,
                    "hashtags": job.hashtags,
                    "scheduled_time": job.scheduled_time.isoformat()
                }
                
                publish_result = await platform_api.publish_content(upload_result, publish_data)
                
                # Update job with results
                job.platform_post_id = publish_result.get("platform_post_id")
                job.platform_url = publish_result.get("platform_url")
                job.status = DistributionStatus.PUBLISHED
                job.published_at = datetime.now()
                
                # Update Redis
                await self.redis_client.hset(
                    f"distribution:job:{job_id}",
                    mapping={
                        "status": job.status.value,
                        "platform_post_id": job.platform_post_id or "",
                        "platform_url": job.platform_url or "",
                        "published_at": job.published_at.isoformat()
                    }
                )
                
                logger.info(f"Distribution job {job_id} executed successfully on {job.platform.value}")
                return True
                
            except Exception as e:
                # Handle execution error
                job.status = DistributionStatus.FAILED
                job.error_message = str(e)
                job.retry_count += 1
                
                # Retry logic
                if job.retry_count < 3:
                    # Reschedule for retry
                    retry_delay = timedelta(minutes=30 * job.retry_count)
                    job.scheduled_time = datetime.now() + retry_delay
                    job.status = DistributionStatus.SCHEDULED
                    self.job_queue.append(job_id)
                
                await self.redis_client.hset(
                    f"distribution:job:{job_id}",
                    mapping={
                        "status": job.status.value,
                        "error_message": job.error_message,
                        "retry_count": str(job.retry_count)
                    }
                )
                
                logger.error(f"Distribution job {job_id} failed: {e}")
                return False
                
            finally:
                self.processing_jobs.discard(job_id)
                
        except Exception as e:
            logger.error(f"Error executing distribution job {job_id}: {e}")
            return False
    
    async def process_distribution_queue(self) -> None:
        """Traiter la queue de distribution"""
        try:
            while self.job_queue:
                job_id = self.job_queue.popleft()
                
                if job_id not in self.processing_jobs:
                    success = await self.execute_distribution_job(job_id)
                    
                    if success:
                        logger.info(f"Successfully processed distribution job: {job_id}")
                    
                    # Add delay between jobs to respect rate limits
                    await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error processing distribution queue: {e}")
    
    async def collect_performance_metrics(self, job_id: str) -> Dict[str, Any]:
        """Collecter les métriques de performance"""
        try:
            if job_id not in self.distribution_jobs:
                return {"error": "Job not found"}
            
            job = self.distribution_jobs[job_id]
            
            if job.status != DistributionStatus.PUBLISHED or not job.platform_post_id:
                return {"error": "Content not published yet"}
            
            # Get platform API
            platform_api = self.platform_apis.get(job.platform)
            if not platform_api:
                return {"error": "Platform API not available"}
            
            # Collect metrics
            metrics = await platform_api.get_performance_metrics(job.platform_post_id)
            
            # Add timestamp and job info
            performance_data = {
                "job_id": job_id,
                "platform": job.platform.value,
                "content_id": job.content_id,
                "platform_post_id": job.platform_post_id,
                "published_at": job.published_at.isoformat() if job.published_at else "",
                "collected_at": datetime.now().isoformat(),
                "metrics": metrics
            }
            
            # Update job metrics
            job.performance_metrics = metrics
            
            # Store in Redis
            await self.redis_client.hset(
                f"distribution:metrics:{job_id}",
                mapping={
                    "platform": job.platform.value,
                    "metrics": json.dumps(metrics),
                    "collected_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Performance metrics collected for job {job_id}")
            return performance_data
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_distribution_analytics(self, creator_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Obtenir les analytics de distribution"""
        try:
            # Get creator's distribution jobs
            creator_jobs = [
                job for job in self.distribution_jobs.values()
                if job.creator_id == creator_id and 
                job.created_at >= datetime.now() - timedelta(days=period_days)
            ]
            
            if not creator_jobs:
                return {"message": "No distribution data found"}
            
            # Platform distribution
            platform_stats = defaultdict(int)
            status_stats = defaultdict(int)
            
            for job in creator_jobs:
                platform_stats[job.platform.value] += 1
                status_stats[job.status.value] += 1
            
            # Performance aggregation
            total_metrics = {
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_reach": 0
            }
            
            for job in creator_jobs:
                if job.performance_metrics:
                    total_metrics["total_views"] += job.performance_metrics.get("views", 0)
                    total_metrics["total_likes"] += job.performance_metrics.get("likes", 0)
                    total_metrics["total_comments"] += job.performance_metrics.get("comments", 0)
                    total_metrics["total_shares"] += job.performance_metrics.get("shares", 0)
                    total_metrics["total_reach"] += job.performance_metrics.get("reach", 0)
            
            # Success rate
            published_jobs = [job for job in creator_jobs if job.status == DistributionStatus.PUBLISHED]
            success_rate = (len(published_jobs) / len(creator_jobs)) * 100 if creator_jobs else 0
            
            # Top performing content
            top_performing = sorted(
                [job for job in creator_jobs if job.performance_metrics],
                key=lambda j: j.performance_metrics.get("views", 0) + j.performance_metrics.get("likes", 0),
                reverse=True
            )[:5]
            
            analytics = {
                "creator_id": creator_id,
                "period_days": period_days,
                "summary": {
                    "total_distributions": len(creator_jobs),
                    "successful_distributions": len(published_jobs),
                    "success_rate": round(success_rate, 2),
                    "platforms_used": len(platform_stats)
                },
                "platform_distribution": dict(platform_stats),
                "status_distribution": dict(status_stats),
                "performance_metrics": total_metrics,
                "top_performing_content": [
                    {
                        "job_id": job.job_id,
                        "platform": job.platform.value,
                        "title": job.title,
                        "views": job.performance_metrics.get("views", 0),
                        "engagement": job.performance_metrics.get("likes", 0) + job.performance_metrics.get("comments", 0)
                    } for job in top_performing
                ],
                "recommendations": await self._generate_distribution_recommendations(creator_jobs)
            }
            
            logger.info(f"Distribution analytics generated for creator {creator_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting distribution analytics: {e}")
            return {"error": str(e)}
    
    async def _generate_distribution_recommendations(self, jobs: List[DistributionJob]) -> List[str]:
        """Générer des recommandations de distribution"""
        recommendations = []
        
        # Platform performance analysis
        platform_performance = defaultdict(list)
        for job in jobs:
            if job.performance_metrics and job.status == DistributionStatus.PUBLISHED:
                engagement = job.performance_metrics.get("likes", 0) + job.performance_metrics.get("comments", 0)
                views = job.performance_metrics.get("views", 1)
                engagement_rate = (engagement / views) * 100 if views > 0 else 0
                platform_performance[job.platform].append(engagement_rate)
        
        # Find best performing platforms
        avg_performance = {}
        for platform, rates in platform_performance.items():
            if rates:
                avg_performance[platform] = statistics.mean(rates)
        
        if avg_performance:
            best_platform = max(avg_performance, key=avg_performance.get)
            recommendations.append(f"Focus more on {best_platform.value} - highest engagement rate ({avg_performance[best_platform]:.1f}%)")
        
        # Timing analysis
        published_jobs = [job for job in jobs if job.status == DistributionStatus.PUBLISHED]
        if published_jobs:
            publish_hours = [job.published_at.hour for job in published_jobs if job.published_at]
            if publish_hours:
                optimal_hour = statistics.mode(publish_hours)
                recommendations.append(f"Optimal posting time: {optimal_hour}:00 - based on your publishing history")
        
        # Content type analysis
        failed_jobs = [job for job in jobs if job.status == DistributionStatus.FAILED]
        if len(failed_jobs) > len(jobs) * 0.1:  # More than 10% failure rate
            recommendations.append("High failure rate detected - check content format and platform guidelines")
        
        return recommendations[:5]  # Limit to 5 recommendations

# Export
__all__ = [
    'DistributionOrchestrator',
    'Platform',
    'ContentFormat',
    'DistributionStatus',
    'AudienceSegment',
    'PlatformConfig',
    'ContentAsset',
    'DistributionJob',
    'DistributionCampaign'
]