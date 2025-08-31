"""Platform Entity Extractor - Specialized Module

Advanced platform-specific entity extraction for social media, streaming, and content
distribution platforms. Identifies platform handles, content IDs, URLs, metrics,
and platform-specific metadata for multi-channel content strategy optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de

Team Specializations:
- Lead AI Developer: Advanced ML/NLP architectures
- Backend Senior: Enterprise-grade scalable systems  
- ML Engineer: Production ML pipelines & optimization
- Database Administrator: High-performance data architecture
- Security Expert: Advanced cybersecurity & protection
- Microservices Architect: Distributed systems design
- Audio Engineer: Professional audio processing
- DevOps Engineer: CI/CD & infrastructure automation
- IA Prompt Engineer: Advanced AI prompt optimization
"""
import asyncio
import re
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from urllib.parse import urlparse, parse_qs

import spacy
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.content import ContentType, ContentMetadata
from ...models.entities import EntityType, Entity
from ...utils.text_processors import TextPreprocessor
from ...utils.validation import validate_input


class PlatformType(Enum):
    """Supported social media and content platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    TWITCH = "twitch"
    DISCORD = "discord"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    GITHUB = "github"
    DEVIANTART = "deviantart"
    FLICKR = "flickr"
    VIMEO = "vimeo"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    UNKNOWN = "unknown"


class PlatformEntityType(Enum):
    """Types of platform-specific entities"""
    HANDLE = "handle"
    CHANNEL_ID = "channel_id"
    CONTENT_ID = "content_id"
    HASHTAG = "hashtag"
    MENTION = "mention"
    URL = "url"
    PLAYLIST_ID = "playlist_id"
    ALBUM_ID = "album_id"
    TRACK_ID = "track_id"
    VIDEO_ID = "video_id"
    POST_ID = "post_id"
    LIVE_STREAM = "live_stream"
    STORY_ID = "story_id"
    REEL_ID = "reel_id"
    SHORT_ID = "short_id"
    COMMUNITY_ID = "community_id"
    GROUP_ID = "group_id"
    PAGE_ID = "page_id"
    PROFILE_ID = "profile_id"


@dataclass
class PlatformEntity:
    """Platform-specific entity with metadata"""
    text: str
    entity_type: PlatformEntityType
    platform: PlatformType
    confidence: float
    start_pos: int
    end_pos: int
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    verified: bool = False
    follower_count: Optional[int] = None
    content_count: Optional[int] = None
    last_activity: Optional[datetime] = None
    extracted_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlatformExtractionResult:
    """Complete platform entity extraction results"""
    entities: List[PlatformEntity]
    platforms_detected: Set[PlatformType]
    total_entities: int
    confidence_avg: float
    extraction_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformEntityExtractor(BaseService):
    """
    Advanced platform entity extractor for social media and content platforms.
    
    Specializes in:
    - Multi-platform handle detection
    - Content ID extraction (videos, tracks, posts)
    - URL parsing and validation
    - Engagement metrics extraction
    - Cross-platform entity linking
    - Platform-specific pattern recognition
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("platform_entity_extractor")
        
        # Platform-specific regex patterns
        self._platform_patterns = self._initialize_platform_patterns()
        
        # Load models
        self._load_models()
        
        # Cache configuration
        self.cache_ttl = config.get("cache_ttl", 3600) if config else 3600
        
    def _initialize_platform_patterns(self) -> Dict[PlatformType, Dict[str, re.Pattern]]:
        """Initialize regex patterns for each platform"""
        patterns = {
            PlatformType.YOUTUBE: {
                "channel_id": re.compile(r"UC[a-zA-Z0-9_-]{22}", re.IGNORECASE),
                "video_id": re.compile(r"[a-zA-Z0-9_-]{11}", re.IGNORECASE),
                "playlist_id": re.compile(r"PL[a-zA-Z0-9_-]{32}", re.IGNORECASE),
                "handle": re.compile(r"@[a-zA-Z0-9_.-]+", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?(?:www\.)?"
                    r"(?:youtube\.com|youtu\.be|m\.youtube\.com)"
                    r"(?:/watch\?v=|/embed/|/v/|\.be/|/watch\?.*&v=)"
                    r"([a-zA-Z0-9_-]{11})",
                    re.IGNORECASE
                ),
                "shorts_url": re.compile(
                    r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
                    re.IGNORECASE
                )
            },
            PlatformType.INSTAGRAM: {
                "handle": re.compile(r"@[a-zA-Z0-9_.]+", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)",
                    re.IGNORECASE
                ),
                "post_id": re.compile(r"[a-zA-Z0-9_-]{11}", re.IGNORECASE),
                "reel_id": re.compile(r"[a-zA-Z0-9_-]{11}", re.IGNORECASE),
                "story_id": re.compile(r"[a-zA-Z0-9_-]{11}", re.IGNORECASE)
            },
            PlatformType.TIKTOK: {
                "handle": re.compile(r"@[a-zA-Z0-9_.]+", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?(?:www\.)?tiktok\.com/@([a-zA-Z0-9_.]+)",
                    re.IGNORECASE
                ),
                "video_id": re.compile(r"[0-9]{19}", re.IGNORECASE)
            },
            PlatformType.TWITTER: {
                "handle": re.compile(r"@[a-zA-Z0-9_]+", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)",
                    re.IGNORECASE
                ),
                "tweet_id": re.compile(r"[0-9]{19}", re.IGNORECASE)
            },
            PlatformType.SPOTIFY: {
                "track_id": re.compile(r"[a-zA-Z0-9]{22}", re.IGNORECASE),
                "album_id": re.compile(r"[a-zA-Z0-9]{22}", re.IGNORECASE),
                "artist_id": re.compile(r"[a-zA-Z0-9]{22}", re.IGNORECASE),
                "playlist_id": re.compile(r"[a-zA-Z0-9]{22}", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?open\.spotify\.com/(track|album|artist|playlist)/([a-zA-Z0-9]{22})",
                    re.IGNORECASE
                )
            },
            PlatformType.SOUNDCLOUD: {
                "url": re.compile(
                    r"(?:https?://)?soundcloud\.com/([a-zA-Z0-9-_.]+)/([a-zA-Z0-9-_.]+)",
                    re.IGNORECASE
                ),
                "handle": re.compile(r"[a-zA-Z0-9-_.]+", re.IGNORECASE)
            },
            PlatformType.TWITCH: {
                "handle": re.compile(r"[a-zA-Z0-9_]+", re.IGNORECASE),
                "url": re.compile(
                    r"(?:https?://)?(?:www\.)?twitch\.tv/([a-zA-Z0-9_]+)",
                    re.IGNORECASE
                )
            },
            PlatformType.LINKEDIN: {
                "profile_url": re.compile(
                    r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)",
                    re.IGNORECASE
                ),
                "company_url": re.compile(
                    r"(?:https?://)?(?:www\.)?linkedin\.com/company/([a-zA-Z0-9-]+)",
                    re.IGNORECASE
                )
            }
        }
        
        # Universal patterns
        hashtag_pattern = re.compile(r"#[a-zA-Z0-9_]+", re.IGNORECASE)
        mention_pattern = re.compile(r"@[a-zA-Z0-9_.]+", re.IGNORECASE)
        
        for platform in patterns:
            patterns[platform]["hashtag"] = hashtag_pattern
            patterns[platform]["mention"] = mention_pattern
            
        return patterns
    
    def _load_models(self):
        """Load ML models for platform detection and entity classification"""
        try:
            # Platform classifier for ambiguous URLs
            self.platform_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # URL validation model
            self.url_validator = pipeline(
                "text-classification",
                model="distilbert-base-uncased",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.models_loaded = True
            self.logger.info("Platform entity extraction models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            self.models_loaded = False
    
    @cache_manager.cached(ttl=3600)
    async def extract_platform_entities(
        self, 
        text: str,
        platforms: Optional[List[PlatformType]] = None,
        include_metrics: bool = True
    ) -> PlatformExtractionResult:
        """
        Extract all platform entities from text
        
        Args:
            text: Input text to analyze
            platforms: Specific platforms to focus on (None for all)
            include_metrics: Whether to fetch engagement metrics
            
        Returns:
            Complete platform extraction results
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not validate_input(text, str):
                raise ValueError("Invalid text input")
            
            # Preprocess text
            processed_text = TextPreprocessor.clean_text(text)
            
            # Extract entities for each platform
            all_entities = []
            detected_platforms = set()
            
            target_platforms = platforms or list(PlatformType)
            
            for platform in target_platforms:
                if platform == PlatformType.UNKNOWN:
                    continue
                    
                entities = await self._extract_platform_specific_entities(
                    processed_text, platform, include_metrics
                )
                
                if entities:
                    all_entities.extend(entities)
                    detected_platforms.add(platform)
            
            # Remove duplicates and resolve conflicts
            unique_entities = await self._deduplicate_entities(all_entities)
            
            # Calculate metrics
            total_entities = len(unique_entities)
            confidence_avg = (
                sum(entity.confidence for entity in unique_entities) / total_entities
                if total_entities > 0 else 0.0
            )
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            await self.metrics.increment("platform_entities_extracted", total_entities)
            await self.metrics.record("extraction_time", extraction_time)
            
            result = PlatformExtractionResult(
                entities=unique_entities,
                platforms_detected=detected_platforms,
                total_entities=total_entities,
                confidence_avg=confidence_avg,
                extraction_time=extraction_time,
                metadata={
                    "text_length": len(text),
                    "processed_length": len(processed_text),
                    "platforms_searched": len(target_platforms)
                }
            )
            
            self.logger.info(
                f"Extracted {total_entities} platform entities from {len(detected_platforms)} platforms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Platform entity extraction failed: {e}")
            await self.metrics.increment("extraction_errors")
            raise
    
    async def _extract_platform_specific_entities(
        self,
        text: str,
        platform: PlatformType,
        include_metrics: bool = True
    ) -> List[PlatformEntity]:
        """Extract entities specific to one platform"""
        entities = []
        
        try:
            patterns = self._platform_patterns.get(platform, {})
            
            for entity_type, pattern in patterns.items():
                matches = pattern.finditer(text)
                
                for match in matches:
                    entity = await self._create_platform_entity(
                        match, entity_type, platform, text, include_metrics
                    )
                    if entity:
                        entities.append(entity)
            
            # Special handling for URLs
            entities.extend(
                await self._extract_platform_urls(text, platform, include_metrics)
            )
            
        except Exception as e:
            self.logger.error(f"Platform-specific extraction failed for {platform}: {e}")
        
        return entities
    
    async def _create_platform_entity(
        self,
        match: re.Match,
        entity_type: str,
        platform: PlatformType,
        full_text: str,
        include_metrics: bool
    ) -> Optional[PlatformEntity]:
        """Create platform entity from regex match"""
        try:
            # Determine entity type enum
            try:
                platform_entity_type = PlatformEntityType(entity_type)
            except ValueError:
                # Handle special cases or create generic type
                platform_entity_type = PlatformEntityType.URL if "url" in entity_type else PlatformEntityType.HANDLE
            
            # Extract metadata from match
            metadata = await self._extract_entity_metadata(match, platform, entity_type)
            
            # Calculate confidence based on pattern strength and context
            confidence = await self._calculate_entity_confidence(
                match, platform, entity_type, full_text
            )
            
            entity = PlatformEntity(
                text=match.group(0),
                entity_type=platform_entity_type,
                platform=platform,
                confidence=confidence,
                start_pos=match.start(),
                end_pos=match.end(),
                url=self._construct_full_url(match, platform, entity_type),
                metadata=metadata
            )
            
            # Fetch engagement metrics if requested
            if include_metrics and entity.url:
                entity.engagement_metrics = await self._fetch_engagement_metrics(
                    entity.url, platform
                )
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to create platform entity: {e}")
            return None
    
    async def _extract_platform_urls(
        self,
        text: str,
        platform: PlatformType,
        include_metrics: bool
    ) -> List[PlatformEntity]:
        """Extract and validate platform URLs"""
        entities = []
        
        # Generic URL pattern
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            re.IGNORECASE
        )
        
        matches = url_pattern.finditer(text)
        
        for match in matches:
            url = match.group(0)
            
            # Check if URL belongs to this platform
            if await self._is_platform_url(url, platform):
                entity = await self._create_url_entity(
                    match, platform, text, include_metrics
                )
                if entity:
                    entities.append(entity)
        
        return entities
    
    async def _is_platform_url(self, url: str, platform: PlatformType) -> bool:
        """Check if URL belongs to specified platform"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            platform_domains = {
                PlatformType.YOUTUBE: ["youtube.com", "youtu.be", "m.youtube.com"],
                PlatformType.INSTAGRAM: ["instagram.com", "www.instagram.com"],
                PlatformType.TIKTOK: ["tiktok.com", "www.tiktok.com"],
                PlatformType.TWITTER: ["twitter.com", "x.com", "www.twitter.com", "www.x.com"],
                PlatformType.SPOTIFY: ["open.spotify.com", "spotify.com"],
                PlatformType.SOUNDCLOUD: ["soundcloud.com", "www.soundcloud.com"],
                PlatformType.TWITCH: ["twitch.tv", "www.twitch.tv"],
                PlatformType.LINKEDIN: ["linkedin.com", "www.linkedin.com"]
            }
            
            return any(
                domain.endswith(d) for d in platform_domains.get(platform, [])
            )
            
        except Exception as e:
            self.logger.error(f"URL validation failed: {e}")
            return False
    
    async def _create_url_entity(
        self,
        match: re.Match,
        platform: PlatformType,
        full_text: str,
        include_metrics: bool
    ) -> Optional[PlatformEntity]:
        """Create platform entity from URL match"""
        try:
            url = match.group(0)
            parsed = urlparse(url)
            
            # Extract ID from URL
            content_id = await self._extract_content_id_from_url(url, platform)
            
            # Determine entity type from URL structure
            entity_type = await self._determine_url_entity_type(url, platform)
            
            confidence = 0.9  # URLs have high confidence
            
            metadata = {
                "domain": parsed.netloc,
                "path": parsed.path,
                "query_params": dict(parse_qs(parsed.query)),
                "content_id": content_id
            }
            
            entity = PlatformEntity(
                text=url,
                entity_type=entity_type,
                platform=platform,
                confidence=confidence,
                start_pos=match.start(),
                end_pos=match.end(),
                url=url,
                metadata=metadata
            )
            
            # Fetch metrics if requested
            if include_metrics:
                entity.engagement_metrics = await self._fetch_engagement_metrics(
                    url, platform
                )
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to create URL entity: {e}")
            return None
    
    async def _extract_content_id_from_url(
        self, 
        url: str, 
        platform: PlatformType
    ) -> Optional[str]:
        """Extract content ID from platform URL"""
        try:
            parsed = urlparse(url)
            
            if platform == PlatformType.YOUTUBE:
                # YouTube video ID extraction
                if "watch" in parsed.path:
                    return parse_qs(parsed.query).get("v", [None])[0]
                elif "/embed/" in parsed.path or "/v/" in parsed.path:
                    return parsed.path.split("/")[-1]
                elif "youtu.be" in parsed.netloc:
                    return parsed.path[1:]  # Remove leading slash
            
            elif platform == PlatformType.SPOTIFY:
                # Spotify content ID extraction
                path_parts = parsed.path.split("/")
                if len(path_parts) >= 3:
                    return path_parts[2]  # track/album/artist ID
            
            elif platform == PlatformType.INSTAGRAM:
                # Instagram post/reel ID extraction
                path_parts = parsed.path.split("/")
                if "p" in path_parts or "reel" in path_parts:
                    idx = path_parts.index("p") if "p" in path_parts else path_parts.index("reel")
                    if idx + 1 < len(path_parts):
                        return path_parts[idx + 1]
            
            # Add more platform-specific extraction logic as needed
            
        except Exception as e:
            self.logger.error(f"Content ID extraction failed: {e}")
        
        return None
    
    async def _determine_url_entity_type(
        self, 
        url: str, 
        platform: PlatformType
    ) -> PlatformEntityType:
        """Determine entity type from URL structure"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if platform == PlatformType.YOUTUBE:
                if "/watch" in path or "/embed/" in path or "/v/" in path:
                    return PlatformEntityType.VIDEO_ID
                elif "/playlist" in path:
                    return PlatformEntityType.PLAYLIST_ID
                elif "/channel/" in path or "/c/" in path or "/user/" in path:
                    return PlatformEntityType.CHANNEL_ID
                elif "/shorts/" in path:
                    return PlatformEntityType.SHORT_ID
            
            elif platform == PlatformType.SPOTIFY:
                if "/track/" in path:
                    return PlatformEntityType.TRACK_ID
                elif "/album/" in path:
                    return PlatformEntityType.ALBUM_ID
                elif "/playlist/" in path:
                    return PlatformEntityType.PLAYLIST_ID
                elif "/artist/" in path:
                    return PlatformEntityType.PROFILE_ID
            
            elif platform == PlatformType.INSTAGRAM:
                if "/p/" in path:
                    return PlatformEntityType.POST_ID
                elif "/reel/" in path:
                    return PlatformEntityType.REEL_ID
                elif "/stories/" in path:
                    return PlatformEntityType.STORY_ID
                else:
                    return PlatformEntityType.PROFILE_ID
            
            # Default to URL type
            return PlatformEntityType.URL
            
        except Exception as e:
            self.logger.error(f"Entity type determination failed: {e}")
            return PlatformEntityType.URL
    
    async def _extract_entity_metadata(
        self,
        match: re.Match,
        platform: PlatformType,
        entity_type: str
    ) -> Dict[str, Any]:
        """Extract additional metadata from entity match"""
        metadata = {
            "platform": platform.value,
            "entity_type": entity_type,
            "match_length": len(match.group(0)),
            "extracted_at": datetime.now().isoformat()
        }
        
        # Platform-specific metadata extraction
        if platform == PlatformType.TWITTER and entity_type == "handle":
            # Twitter handle metadata
            handle = match.group(0).replace("@", "")
            metadata.update({
                "handle_length": len(handle),
                "has_underscore": "_" in handle,
                "is_numeric": handle.isdigit()
            })
        
        elif platform == PlatformType.YOUTUBE and entity_type == "video_id":
            # YouTube video metadata
            video_id = match.group(0)
            metadata.update({
                "video_id_length": len(video_id),
                "contains_special_chars": any(c in video_id for c in "-_")
            })
        
        return metadata
    
    async def _calculate_entity_confidence(
        self,
        match: re.Match,
        platform: PlatformType,
        entity_type: str,
        full_text: str
    ) -> float:
        """Calculate confidence score for extracted entity"""
        base_confidence = 0.7
        
        # Pattern strength bonus
        pattern_strength = {
            "url": 0.9,
            "channel_id": 0.85,
            "video_id": 0.8,
            "handle": 0.75,
            "hashtag": 0.7
        }
        
        confidence = pattern_strength.get(entity_type, base_confidence)
        
        # Context analysis bonus
        context_start = max(0, match.start() - 50)
        context_end = min(len(full_text), match.end() + 50)
        context = full_text[context_start:context_end].lower()
        
        # Platform-specific context keywords
        platform_keywords = {
            PlatformType.YOUTUBE: ["youtube", "video", "channel", "subscribe", "watch"],
            PlatformType.INSTAGRAM: ["instagram", "insta", "post", "story", "reel"],
            PlatformType.TIKTOK: ["tiktok", "viral", "trending", "fyp"],
            PlatformType.TWITTER: ["twitter", "tweet", "retweet", "follow"],
            PlatformType.SPOTIFY: ["spotify", "music", "song", "album", "artist"]
        }
        
        keywords = platform_keywords.get(platform, [])
        keyword_bonus = sum(0.05 for keyword in keywords if keyword in context)
        confidence = min(0.95, confidence + keyword_bonus)
        
        # Length penalty for very short matches
        if len(match.group(0)) < 3:
            confidence *= 0.8
        
        return confidence
    
    def _construct_full_url(
        self,
        match: re.Match,
        platform: PlatformType,
        entity_type: str
    ) -> Optional[str]:
        """Construct full URL from extracted entity"""
        try:
            text = match.group(0)
            
            # If already a URL, return as-is
            if text.startswith("http"):
                return text
            
            # Platform-specific URL construction
            if platform == PlatformType.YOUTUBE:
                if entity_type == "video_id":
                    return f"https://youtube.com/watch?v={text}"
                elif entity_type == "channel_id":
                    return f"https://youtube.com/channel/{text}"
                elif entity_type == "handle":
                    return f"https://youtube.com/{text}"
            
            elif platform == PlatformType.INSTAGRAM:
                if entity_type == "handle":
                    handle = text.replace("@", "")
                    return f"https://instagram.com/{handle}"
            
            elif platform == PlatformType.TWITTER:
                if entity_type == "handle":
                    handle = text.replace("@", "")
                    return f"https://twitter.com/{handle}"
            
            elif platform == PlatformType.SPOTIFY:
                if entity_type == "track_id":
                    return f"https://open.spotify.com/track/{text}"
                elif entity_type == "album_id":
                    return f"https://open.spotify.com/album/{text}"
            
            # Add more platform-specific URL construction as needed
            
        except Exception as e:
            self.logger.error(f"URL construction failed: {e}")
        
        return None
    
    async def _fetch_engagement_metrics(
        self,
        url: str,
        platform: PlatformType
    ) -> Dict[str, int]:
        """Fetch comprehensive engagement metrics for platform content"""
        try:
            # Initialize metrics structure
            metrics = {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "followers": 0,
                "engagement_rate": 0.0,
                "last_updated": datetime.now().isoformat()
            }
            
            # Platform-specific API integration
            if platform == PlatformType.YOUTUBE:
                metrics.update(await self._fetch_youtube_api_metrics(url))
            elif platform == PlatformType.INSTAGRAM:
                metrics.update(await self._fetch_instagram_api_metrics(url))
            elif platform == PlatformType.TIKTOK:
                metrics.update(await self._fetch_tiktok_api_metrics(url))
            elif platform == PlatformType.SPOTIFY:
                metrics.update(await self._fetch_spotify_api_metrics(url))
            elif platform == PlatformType.TWITTER:
                metrics.update(await self._fetch_twitter_api_metrics(url))
            elif platform == PlatformType.LINKEDIN:
                metrics.update(await self._fetch_linkedin_api_metrics(url))
            elif platform == PlatformType.FACEBOOK:
                metrics.update(await self._fetch_facebook_api_metrics(url))
            elif platform == PlatformType.SOUNDCLOUD:
                metrics.update(await self._fetch_soundcloud_api_metrics(url))
            elif platform == PlatformType.BANDCAMP:
                metrics.update(await self._fetch_bandcamp_metrics(url))
            elif platform == PlatformType.TWITCH:
                metrics.update(await self._fetch_twitch_api_metrics(url))
            
            # Calculate derived metrics
            if metrics.get("likes", 0) > 0 and metrics.get("views", 0) > 0:
                metrics["engagement_rate"] = round(
                    (metrics["likes"] + metrics["comments"]) / metrics["views"] * 100, 2
                )
            
            # Apply rate limiting and caching
            cache_key = f"metrics_{platform.value}_{hash(url)}"
            await cache_manager.set(cache_key, metrics, ttl=3600)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error fetching engagement metrics for {platform.value}: {str(e)}")
            return metrics
    
    async def _fetch_youtube_api_metrics(self, url: str) -> Dict[str, int]:
        """Fetch YouTube API metrics"""
        try:
            # Extract video/channel ID from URL
            video_id = self._extract_youtube_id(url)
            if not video_id:
                return {}
            
            # Simulate YouTube Data API v3 call
            # In production, use actual API with proper authentication
            api_response = await self._make_youtube_api_request(video_id)
            
            return {
                "views": api_response.get("viewCount", 0),
                "likes": api_response.get("likeCount", 0),
                "comments": api_response.get("commentCount", 0),
                "subscribers": api_response.get("subscriberCount", 0),
                "duration": api_response.get("duration", ""),
                "published_at": api_response.get("publishedAt", "")
            }
            
        except Exception as e:
            self.logger.error(f"YouTube API error: {str(e)}")
            return {}
    
    async def _fetch_instagram_api_metrics(self, url: str) -> Dict[str, int]:
        """Fetch Instagram API metrics"""
        try:
            # Extract post/profile ID
            entity_id = self._extract_instagram_id(url)
            if not entity_id:
                return {}
            
            # Simulate Instagram Basic Display API call
            api_response = await self._make_instagram_api_request(entity_id)
            
            return {
                "likes": api_response.get("like_count", 0),
                "comments": api_response.get("comments_count", 0),
                "followers": api_response.get("followers_count", 0),
                "following": api_response.get("follows_count", 0),
                "media_count": api_response.get("media_count", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Instagram API error: {str(e)}")
            return {}
    
    async def _fetch_spotify_api_metrics(self, url: str) -> Dict[str, int]:
        """Fetch Spotify API metrics"""
        try:
            # Extract track/artist/album ID
            entity_id = self._extract_spotify_id(url)
            if not entity_id:
                return {}
            
            # Simulate Spotify Web API call
            api_response = await self._make_spotify_api_request(entity_id)
            
            return {
                "followers": api_response.get("followers", {}).get("total", 0),
                "popularity": api_response.get("popularity", 0),
                "monthly_listeners": api_response.get("monthly_listeners", 0),
                "streams": api_response.get("streams", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Spotify API error: {str(e)}")
            return {}
    
    async def _make_youtube_api_request(self, video_id: str) -> Dict[str, Any]:
        """Simulate YouTube API request - replace with actual implementation"""
        # This is a mock response - implement actual API calls in production
        import random
        return {
            "viewCount": random.randint(1000, 1000000),
            "likeCount": random.randint(10, 50000),
            "commentCount": random.randint(5, 5000),
            "subscriberCount": random.randint(100, 100000),
            "duration": "PT3M45S",
            "publishedAt": "2024-01-01T00:00:00Z"
        }
    
    async def _make_instagram_api_request(self, entity_id: str) -> Dict[str, Any]:
        """Simulate Instagram API request - replace with actual implementation"""
        import random
        return {
            "like_count": random.randint(50, 10000),
            "comments_count": random.randint(5, 1000),
            "followers_count": random.randint(1000, 1000000),
            "follows_count": random.randint(100, 5000),
            "media_count": random.randint(10, 2000)
        }
    
    async def _make_spotify_api_request(self, entity_id: str) -> Dict[str, Any]:
        """Simulate Spotify API request - replace with actual implementation"""
        import random
        return {
            "followers": {"total": random.randint(1000, 5000000)},
            "popularity": random.randint(0, 100),
            "monthly_listeners": random.randint(10000, 10000000),
            "streams": random.randint(100000, 100000000)
        }
    
    async def _deduplicate_entities(
        self, 
        entities: List[PlatformEntity]
    ) -> List[PlatformEntity]:
        """Remove duplicate entities and resolve conflicts"""
        if not entities:
            return []
        
        # Group by text content
        entity_groups = {}
        for entity in entities:
            key = entity.text.lower()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        unique_entities = []
        
        for group in entity_groups.values():
            if len(group) == 1:
                unique_entities.append(group[0])
            else:
                # Resolve conflicts by highest confidence
                best_entity = max(group, key=lambda e: e.confidence)
                
                # Merge metadata from other entities
                for other in group:
                    if other != best_entity:
                        best_entity.metadata.update(other.metadata)
                        
                        # Merge engagement metrics
                        for key, value in other.engagement_metrics.items():
                            if key in best_entity.engagement_metrics:
                                best_entity.engagement_metrics[key] = max(
                                    best_entity.engagement_metrics[key], value
                                )
                            else:
                                best_entity.engagement_metrics[key] = value
                
                unique_entities.append(best_entity)
        
        return unique_entities
    
    async def extract_hashtags(self, text: str) -> List[PlatformEntity]:
        """Extract hashtags from text"""
        hashtag_pattern = re.compile(r"#\w+", re.IGNORECASE)
        hashtags = []
        
        for match in hashtag_pattern.finditer(text):
            entity = PlatformEntity(
                text=match.group(0),
                entity_type=PlatformEntityType.HASHTAG,
                platform=PlatformType.UNKNOWN,
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            )
            hashtags.append(entity)
        
        return hashtags
    
    async def extract_mentions(self, text: str) -> List[PlatformEntity]:
        """Extract mentions from text"""
        mention_pattern = re.compile(r"@\w+", re.IGNORECASE)
        mentions = []
        
        for match in mention_pattern.finditer(text):
            entity = PlatformEntity(
                text=match.group(0),
                entity_type=PlatformEntityType.MENTION,
                platform=PlatformType.UNKNOWN,
                confidence=0.85,
                start_pos=match.start(),
                end_pos=match.end()
            )
            mentions.append(entity)
        
        return mentions
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics by platform"""
        return await self.metrics.get_all_metrics()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health status"""
        return {
            "status": "healthy" if self.models_loaded else "degraded",
            "models_loaded": self.models_loaded,
            "supported_platforms": len(self._platform_patterns),
            "cache_enabled": bool(self.cache_ttl),
            "timestamp": datetime.now().isoformat()
        }
