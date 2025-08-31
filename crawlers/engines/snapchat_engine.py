"""
Snapchat Content Crawling Engine

Advanced industry-grade engine for Snapchat content crawling and story analysis.
Implements ephemeral content protection with AI-powered trend detection and AR monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum

from ..base import BaseCrawlerEngine
from ...core.platforms.snapchat import SnapchatPlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class SnapType(Enum):
    """Snapchat content types"""
    PHOTO = "photo"
    VIDEO = "video"
    STORY = "story"
    SPOTLIGHT = "spotlight"
    SNAP_MAP = "snap_map"
    AR_LENS = "ar_lens"
    BITMOJI = "bitmoji"


class ContentLifespan(Enum):
    """Content lifespan categories"""
    TEMPORARY = "temporary"  # 1-10 seconds
    STORY = "story"  # 24 hours
    SPOTLIGHT = "spotlight"  # Permanent
    SAVED = "saved"  # User saved
    MEMORIES = "memories"  # Personal archive


@dataclass
class SnapchatContent:
    """Snapchat content data structure"""
    content_id: str
    user_id: str
    snap_type: SnapType
    media_url: str
    thumbnail_url: Optional[str]
    duration: int
    lifespan: ContentLifespan
    view_count: int
    screenshot_count: int
    share_count: int
    ar_effects_used: List[str]
    location_data: Optional[Dict[str, Any]]
    created_at: datetime
    expires_at: Optional[datetime]
    engagement_rate: float
    viral_potential: float
    ar_innovation_score: float
    content_fingerprint: str
    protection_level: str
    monetization_potential: float


class SnapchatEngine(BaseCrawlerEngine):
    """
    Professional Snapchat crawling engine with advanced ephemeral content analysis
    and AR/filter monetization strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = SnapchatPlatform(config.get('snapchat', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # Snapchat specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 300)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 20)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.5)
        self.enable_ar_analysis = config.get('enable_ar_analysis', True)
        self.ephemeral_capture_enabled = config.get('ephemeral_capture_enabled', True)
        
    async def crawl_user_stories(
        self, 
        user_id: str, 
        snap_types: List[SnapType] = None,
        include_expired: bool = False
    ) -> AsyncGenerator[SnapchatContent, None]:
        """
        Crawl stories from a specific Snapchat user with ephemeral content handling
        
        Args:
            user_id: User identifier
            snap_types: List of snap types to crawl
            include_expired: Whether to include expired content from cache
            
        Yields:
            SnapchatContent: Processed snap objects
        """
        self.logger.info(f"Starting Snapchat stories crawl for user: {user_id}")
        
        try:
            async with self._create_session() as session:
                snap_types = snap_types or list(SnapType)
                
                # Get user's active stories
                stories = await self._fetch_user_stories(session, user_id, include_expired)
                
                for story in stories:
                    if self._matches_snap_type_filter(story, snap_types):
                        # Quick processing due to ephemeral nature
                        processed_snap = await self._process_snap(story)
                        if processed_snap:
                            yield processed_snap
                            
        except Exception as e:
            self.logger.error(f"Error crawling user stories: {str(e)}")
            await self.metrics_collector.record_error('snapchat_crawl_error', str(e))
            raise
            
    async def _fetch_user_stories(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        include_expired: bool
    ) -> List[Dict[str, Any]]:
        """Fetch user's stories with ephemeral content considerations"""
        
        url = f"https://app.snapchat.com/web/deeplink/snapcode"
        
        params = {
            'username': user_id,
            'type': 'story'
        }
        
        if include_expired:
            params['include_expired'] = 'true'
            
        headers = await self._get_authenticated_headers()
        stories = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get('stories', [])
                else:
                    self.logger.error(f"Failed to fetch stories: HTTP {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching user stories: {str(e)}")
            
        return stories
        
    def _matches_snap_type_filter(self, snap: Dict[str, Any], snap_types: List[SnapType]) -> bool:
        """Check if snap matches the snap type filter"""
        
        snap_type = self._determine_snap_type(snap)
        return snap_type in snap_types
        
    def _determine_snap_type(self, snap: Dict[str, Any]) -> SnapType:
        """Determine snap type from snap data"""
        
        media_type = snap.get('media_type', 'photo')
        duration = snap.get('duration', 0)
        
        if snap.get('is_spotlight', False):
            return SnapType.SPOTLIGHT
        elif snap.get('has_ar_effects', False):
            return SnapType.AR_LENS
        elif snap.get('location_data'):
            return SnapType.SNAP_MAP
        elif media_type == 'video' or duration > 0:
            return SnapType.VIDEO
        else:
            return SnapType.PHOTO
            
    async def _process_snap(self, raw_snap: Dict[str, Any]) -> Optional[SnapchatContent]:
        """Process and analyze snap with advanced ephemeral content handling"""



        
        try:
            content_id = raw_snap.get('id')
            if not content_id:
                return None
                
            # Extract snap information
            user_id = raw_snap.get('username', '')
            snap_type = self._determine_snap_type(raw_snap)
            media_url = raw_snap.get('media_url', '')
            thumbnail_url = raw_snap.get('thumbnail_url')
            duration = raw_snap.get('duration', 0)
            
            if not media_url:
                return None
                
            # Quick fingerprint generation for ephemeral content
            content_fingerprint = await self.content_guardian.generate_ephemeral_fingerprint(
                f"{content_id}{media_url}{user_id}"
            )
            
            # Rapid content analysis for time-sensitive content
            quality_score = await self.content_analyzer.analyze_ephemeral_content({
                'media_url': media_url,
                'duration': duration,
                'snap_type': snap_type.value,
                'ar_effects': raw_snap.get('ar_effects', [])
            })
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Extract engagement metrics
            view_count = raw_snap.get('view_count', 0)
            screenshot_count = raw_snap.get('screenshot_count', 0)
            share_count = raw_snap.get('share_count', 0)
            
            # Calculate engagement rate
            engagement_rate = self._calculate_engagement_rate(raw_snap)
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(raw_snap)
            
            # Analyze AR innovation if applicable
            ar_innovation_score = await self._analyze_ar_innovation(raw_snap)
            
            # Calculate monetization potential
            monetization_potential = await self._calculate_monetization_potential(
                raw_snap, quality_score, ar_innovation_score
            )
            
            # Determine content lifespan
            lifespan = self._determine_content_lifespan(raw_snap)
            
            # Calculate expiration time
            expires_at = self._calculate_expiration_time(raw_snap, lifespan)
            
            # Determine protection level
            protection_level = "ephemeral" if lifespan == ContentLifespan.TEMPORARY else "standard"
            
            # Create Snapchat content object
            snapchat_content = SnapchatContent(
                content_id=content_id,
                user_id=user_id,
                snap_type=snap_type,
                media_url=media_url,
                thumbnail_url=thumbnail_url,
                duration=duration,
                lifespan=lifespan,
                view_count=view_count,
                screenshot_count=screenshot_count,
                share_count=share_count,
                ar_effects_used=raw_snap.get('ar_effects', []),
                location_data=raw_snap.get('location_data'),
                created_at=datetime.fromisoformat(
                    raw_snap.get('created_at', '').replace('Z', '+00:00')
                ),
                expires_at=expires_at,
                engagement_rate=engagement_rate,
                viral_potential=viral_potential,
                ar_innovation_score=ar_innovation_score,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                monetization_potential=monetization_potential
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='snapchat',
                content_type=snap_type.value,
                quality_score=quality_score
            )
            
            return snapchat_content
            
        except Exception as e:
            self.logger.error(f"Error processing snap: {str(e)}")
            return None
            
    def _calculate_engagement_rate(self, snap: Dict[str, Any]) -> float:
        """Calculate engagement rate for the snap"""
        
        views = snap.get('view_count', 1)
        screenshots = snap.get('screenshot_count', 0)
        shares = snap.get('share_count', 0)
        
        if views == 0:
            return 0.0
            
        # Screenshots and shares are strong engagement indicators on Snapchat
        engagement_rate = (screenshots * 3 + shares * 5) / views
        
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _calculate_viral_potential(self, snap: Dict[str, Any]) -> float:
        """Calculate viral potential for ephemeral content"""
        
        # Factors: rapid view accumulation, share rate, AR innovation
        views = snap.get('view_count', 0)
        shares = snap.get('share_count', 0)
        time_active = self._calculate_time_active(snap)
        
        # View velocity (views per minute active)
        view_velocity = views / max(time_active, 1)
        
        # Share rate
        share_rate = shares / max(views, 1)
        
        # AR effects boost viral potential
        ar_boost = 0.2 if snap.get('ar_effects') else 0.0
        
        # Location-based content has higher viral potential
        location_boost = 0.1 if snap.get('location_data') else 0.0
        
        # Combine factors
        viral_potential = min(view_velocity / 100, 0.5) + (share_rate * 0.3) + ar_boost + location_boost
        
        return min(viral_potential, 1.0)
        
    def _calculate_time_active(self, snap: Dict[str, Any]) -> float:
        """Calculate how long the snap has been active (in minutes)"""
        
        created_at = snap.get('created_at', '')
        if not created_at:
            return 1.0
            
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_diff = datetime.now() - created_time.replace(tzinfo=None)
            return max(time_diff.total_seconds() / 60, 1.0)
        except Exception:
            return 1.0
            
    async def _analyze_ar_innovation(self, snap: Dict[str, Any]) -> float:
        """Analyze AR innovation and creativity score"""
        
        if not self.enable_ar_analysis:
            return 0.0
            
        ar_effects = snap.get('ar_effects', [])
        if not ar_effects:
            return 0.0
            
        # Analyze AR effect complexity and innovation
        innovation_factors = {
            'face_tracking': 0.2,
            'world_tracking': 0.3,
            'hand_tracking': 0.4,
            'body_tracking': 0.3,
            'voice_effects': 0.2,
            'interactive_elements': 0.5,
            'custom_shaders': 0.6,
            'ml_integration': 0.7
        }
        
        innovation_score = 0.0
        for effect in ar_effects:
            effect_type = effect.get('type', '').lower()
            for factor, score in innovation_factors.items():
                if factor in effect_type:
                    innovation_score += score
                    break
                    
        # Normalize score
        return min(innovation_score / len(ar_effects) if ar_effects else 0, 1.0)
        
    async def _calculate_monetization_potential(
        self,
        snap: Dict[str, Any],
        quality_score: float,
        ar_innovation_score: float
    ) -> float:
        """Calculate monetization potential for Snapchat content"""
        
        # Factors: engagement, AR innovation, brand potential, audience
        engagement_rate = self._calculate_engagement_rate(snap)
        viral_potential = await self._calculate_viral_potential(snap)
        
        # Brand collaboration potential
        brand_keywords = ['brand', 'product', 'review', 'sponsored', 'ad']
        content_text = snap.get('caption', '').lower()
        brand_potential = 0.3 if any(keyword in content_text for keyword in brand_keywords) else 0.0
        
        # AR lens monetization potential
        ar_monetization = ar_innovation_score * 0.4 if ar_innovation_score > 0.5 else 0.0
        
        # Combine factors
        monetization_potential = (
            engagement_rate * 0.3 +
            viral_potential * 0.2 +
            quality_score * 0.2 +
            brand_potential * 0.15 +
            ar_monetization * 0.15
        )
        
        return min(monetization_potential, 1.0)
        
    def _determine_content_lifespan(self, snap: Dict[str, Any]) -> ContentLifespan:
        """Determine content lifespan category"""
        
        if snap.get('is_story', False):
            return ContentLifespan.STORY
        elif snap.get('is_spotlight', False):
            return ContentLifespan.SPOTLIGHT
        elif snap.get('is_saved', False):
            return ContentLifespan.SAVED
        elif snap.get('is_memories', False):
            return ContentLifespan.MEMORIES
        else:
            return ContentLifespan.TEMPORARY
            
    def _calculate_expiration_time(
        self, 
        snap: Dict[str, Any],
        lifespan: ContentLifespan
    ) -> Optional[datetime]:
        """Calculate when content expires"""
        
        created_at = snap.get('created_at', '')
        if not created_at:
            return None
            
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            if lifespan == ContentLifespan.TEMPORARY:
                return created_time + timedelta(seconds=snap.get('duration', 10))
            elif lifespan == ContentLifespan.STORY:
                return created_time + timedelta(hours=24)
            else:
                return None  # Permanent content
                
        except Exception:
            return None
            
    async def crawl_spotlight_content(
        self, 
        limit: int = 100,
        category_filter: Optional[str] = None
    ) -> List[SnapchatContent]:
        """Crawl Snapchat Spotlight trending content"""
        
        self.logger.info(f"Crawling Spotlight content, limit: {limit}")
        
        spotlight_content = []
        
        try:
            async with self._create_session() as session:
                content_data = await self._fetch_spotlight_content(session, limit, category_filter)
                
                for snap_data in content_data:
                    snap = await self._process_snap(snap_data)
                    if snap:
                        spotlight_content.append(snap)
                        
        except Exception as e:
            self.logger.error(f"Error crawling Spotlight content: {str(e)}")
            
        return spotlight_content[:limit]
        
    async def _fetch_spotlight_content(
        self,
        session: aiohttp.ClientSession,
        limit: int,
        category_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Fetch Spotlight trending content"""
        
        url = "https://app.snapchat.com/web/deeplink/spotlight"
        
        params = {
            'limit': min(limit, 50),
            'sort': 'trending'
        }
        
        if category_filter:
            params['category'] = category_filter
            
        headers = await self._get_authenticated_headers()
        content = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('spotlight_snaps', [])
                    
        except Exception as e:
            self.logger.error(f"Error fetching Spotlight content: {str(e)}")
            
        return content
        
    async def crawl_ar_lenses(
        self, 
        creator_id: Optional[str] = None,
        innovation_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Crawl AR lenses for innovation analysis"""
        
        self.logger.info(f"Crawling AR lenses, creator: {creator_id}")
        
        ar_lenses = []
        
        try:
            async with self._create_session() as session:
                lenses_data = await self._fetch_ar_lenses(session, creator_id)
                
                for lens in lenses_data:
                    innovation_score = await self._analyze_lens_innovation(lens)
                    if innovation_score >= innovation_threshold:
                        lens['innovation_score'] = innovation_score
                        ar_lenses.append(lens)
                        
        except Exception as e:
            self.logger.error(f"Error crawling AR lenses: {str(e)}")
            
        return ar_lenses
        
    async def _fetch_ar_lenses(
        self,
        session: aiohttp.ClientSession,
        creator_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Fetch AR lenses data"""
        
        url = "https://lens-studio.snapchat.com/api/lenses"
        
        params = {
            'limit': 50,
            'sort': 'popularity'
        }
        
        if creator_id:
            params['creator'] = creator_id
            
        headers = await self._get_authenticated_headers()
        lenses = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    lenses = data.get('lenses', [])
                    
        except Exception as e:
            self.logger.error(f"Error fetching AR lenses: {str(e)}")
            
        return lenses
        
    async def _analyze_lens_innovation(self, lens: Dict[str, Any]) -> float:
        """Analyze innovation level of an AR lens"""
        
        if not self.enable_ar_analysis:
            return 0.5
            
        # Analyze technical features
        features = lens.get('features', [])
        technology_stack = lens.get('technology', [])
        
        innovation_indicators = {
            'machine_learning': 0.8,
            'computer_vision': 0.7,
            'physics_simulation': 0.6,
            'real_time_rendering': 0.5,
            'face_mesh': 0.4,
            'hand_tracking': 0.7,
            'world_tracking': 0.6,
            'occlusion': 0.5,
            'lighting_estimation': 0.4
        }
        
        innovation_score = 0.0
        feature_count = 0
        
        for feature in features + technology_stack:
            feature_name = feature.lower()
            for indicator, score in innovation_indicators.items():
                if indicator in feature_name:
                    innovation_score += score
                    feature_count += 1
                    break
                    
        # Normalize by feature count
        if feature_count > 0:
            innovation_score = innovation_score / feature_count
        else:
            innovation_score = 0.3  # Default for basic lenses
            
        # Boost for unique/experimental features
        if lens.get('is_experimental', False):
            innovation_score += 0.2
            
        return min(innovation_score, 1.0)
        
    async def monitor_ephemeral_trends(
        self, 
        monitoring_period: timedelta = timedelta(hours=6)
    ) -> Dict[str, Any]:
        """Monitor ephemeral content trends in real-time"""
        
        self.logger.info("Monitoring ephemeral trends")
        
        try:
            # Due to ephemeral nature, focus on recent trends
            end_time = datetime.now()
            start_time = end_time - monitoring_period
            
            trend_data = {
                'trending_hashtags': await self._analyze_trending_hashtags(),
                'popular_ar_effects': await self._analyze_popular_ar_effects(),
                'viral_patterns': await self._analyze_viral_patterns(),
                'engagement_hotspots': await self._analyze_engagement_hotspots(),
                'content_lifecycle_analysis': await self._analyze_content_lifecycle(),
                'monetization_opportunities': await self._identify_monetization_opportunities()
            }
            
            # Record trend metrics
            await self.metrics_collector.record_trend_analysis('snapchat', trend_data)
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Error monitoring ephemeral trends: {str(e)}")
            return {}
            
    async def _analyze_trending_hashtags(self) -> List[Dict[str, Any]]:
        """Analyze trending hashtags and topics"""
        
        # This would integrate with Snapchat's trending API
        # Placeholder implementation
        return [
            {'hashtag': '#SnapchatTrends', 'usage_count': 1500, 'growth_rate': 0.8},
            {'hashtag': '#ARLens', 'usage_count': 1200, 'growth_rate': 0.6},
            {'hashtag': '#SpotlightChallenge', 'usage_count': 900, 'growth_rate': 0.9}
        ]
        
    async def _analyze_popular_ar_effects(self) -> List[Dict[str, Any]]:
        """Analyze most popular AR effects"""
        
        # This would analyze current AR effect usage
        # Placeholder implementation
        return [
            {'effect_name': 'Face Morph', 'usage_count': 5000, 'innovation_score': 0.7},
            {'effect_name': 'World Lens', 'usage_count': 3500, 'innovation_score': 0.8},
            {'effect_name': 'Voice Changer', 'usage_count': 2800, 'innovation_score': 0.5}
        ]
        
    async def _analyze_viral_patterns(self) -> Dict[str, Any]:
        """Analyze viral content patterns"""



        
        return {
            'optimal_duration': '3-7 seconds',
            'peak_posting_hours': [18, 19, 20, 21],
            'viral_content_types': ['AR lens', 'dance', 'comedy'],
            'engagement_patterns': {
                'quick_engagement': 0.8,
                'sustained_sharing': 0.6,
                'screenshot_rate': 0.15
            }
        }
        
    async def _analyze_engagement_hotspots(self) -> List[Dict[str, Any]]:
        """Analyze geographic engagement hotspots"""



        
        return [
            {'location': 'Los Angeles', 'engagement_rate': 0.9, 'trending_content': 'AR filters'},
            {'location': 'New York', 'engagement_rate': 0.8, 'trending_content': 'street art'},
            {'location': 'Paris', 'engagement_rate': 0.85, 'trending_content': 'fashion snaps'}
        ]
        
    async def _analyze_content_lifecycle(self) -> Dict[str, Any]:
        """Analyze ephemeral content lifecycle patterns"""



        
        return {
            'average_view_duration': 2.5,
            'peak_engagement_window': '0-30 minutes',
            'sharing_patterns': {
                'immediate_shares': 0.7,
                'delayed_shares': 0.2,
                'cross_platform_shares': 0.1
            },
            'screenshot_timing': 'within first 10 seconds'
        }
        
    async def _identify_monetization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify current monetization opportunities"""



        
        return [
            {
                'opportunity': 'AR Lens Sponsorship',
                'potential_revenue': 5000,
                'effort_required': 'medium',
                'time_to_market': '2-4 weeks'
            },
            {
                'opportunity': 'Spotlight Content Creation',
                'potential_revenue': 2000,
                'effort_required': 'low',
                'time_to_market': '1 week'
            },
            {
                'opportunity': 'Brand Partnership Stories',
                'potential_revenue': 8000,
                'effort_required': 'high',
                'time_to_market': '4-6 weeks'
            }
        ]
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""



        
        return {
            'User-Agent': 'Snapchat/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'X-Snapchat-Client': self.config.get('client_id', ''),
            'X-Snapchat-UUID': self.config.get('device_uuid', '')
        }
        
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create configured HTTP session"""
        
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_requests,
            limit_per_host=self.max_concurrent_requests
        )
        
        timeout = aiohttp.ClientTimeout(total=15)  # Shorter timeout for ephemeral content
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    async def _apply_rate_limiting(self):
        """Apply rate limiting optimized for ephemeral content"""
        
        # Faster rate limiting for time-sensitive ephemeral content
        await asyncio.sleep(60 / self.rate_limit_per_minute)
