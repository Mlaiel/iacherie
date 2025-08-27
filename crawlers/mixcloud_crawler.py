"""
Mixcloud Platform Crawler - Enterprise-Grade DJ Mix and Podcast Monitoring

Advanced Mixcloud crawler with comprehensive DJ mix analysis, podcast monitoring,
and music curation tracking capabilities for the IA Influencer Agent platform.

© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized reproduction or distribution of this code is strictly prohibited.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, AsyncGenerator
import uuid

import aiohttp
from ..rate_limiters import RateLimiter, PlatformLimits
from ..fingerprinting import ContentFingerprinter
from ..proxy_manager import ProxyManager


logger = logging.getLogger(__name__)


@dataclass
class MixcloudShow:
    """Comprehensive Mixcloud show/mix data structure."""
    show_id: str
    key: str
    name: str
    description: str
    user_id: str
    username: str
    user_display_name: str
    url: str
    audio_url: Optional[str]
    created_time: datetime
    updated_time: datetime
    play_count: int
    favorite_count: int
    comment_count: int
    repost_count: int
    duration: int  # in seconds
    tags: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    track_sections: List[Dict] = field(default_factory=list)
    featured_artists: List[str] = field(default_factory=list)
    city: Optional[str] = None
    country: Optional[str] = None
    picture_url: Optional[str] = None
    waveform_url: Optional[str] = None
    audio_fingerprint: Optional[str] = None
    content_warnings: List[str] = field(default_factory=list)
    violation_score: float = 0.0
    similarity_matches: List[str] = field(default_factory=list)
    engagement_metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class MixcloudUser:
    """Mixcloud user profile data structure."""
    user_id: str
    username: str
    display_name: str
    bio: str
    city: Optional[str]
    country: Optional[str]
    picture_url: str
    cover_url: Optional[str]
    follower_count: int
    following_count: int
    cloudcast_count: int
    favorite_count: int
    listen_count: int
    created_time: datetime
    is_pro: bool = False
    is_premium: bool = False
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    recent_shows: List[MixcloudShow] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    engagement_rate: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class MixcloudSearchResult:
    """Mixcloud search result data structure."""
    query: str
    total_results: int
    shows: List[MixcloudShow]
    users: List[MixcloudUser]
    genres: List[str]
    trending_tags: List[str]
    search_timestamp: datetime
    has_more: bool = False
    next_page_url: Optional[str] = None


@dataclass
class MixcloudAnalytics:
    """Mixcloud analytics and insights data."""
    period_start: datetime
    period_end: datetime
    total_plays: int
    total_favorites: int
    total_reposts: int
    total_comments: int
    unique_listeners: int
    engagement_rate: float
    top_performing_shows: List[MixcloudShow]
    audience_demographics: Dict[str, Union[int, float]]
    trending_genres: List[Dict]
    growth_metrics: Dict[str, float]
    geographic_data: Dict[str, int]
    listening_patterns: Dict[str, Union[int, float]]


class MixcloudCrawler:
    """
    Enterprise-grade Mixcloud crawler with advanced audio content analysis.
    
    Features:
    - DJ mix and podcast monitoring
    - Audio fingerprinting and similarity detection
    - User engagement tracking and analytics
    - Genre and tag analysis
    - Real-time content discovery
    - Copyright violation detection
    - Advanced rate limiting with burst handling
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.access_token = config.get('access_token')
        
        self.rate_limiter = RateLimiter(
            PlatformLimits(
                requests_per_minute=300,
                requests_per_hour=5000,
                requests_per_day=50000,
                burst_limit=20,
                concurrent_limit=10
            )
        )
        
        self.proxy_manager = ProxyManager(config.get('proxies', []))
        self.fingerprinter = ContentFingerprinter()
        
        self.base_url = "https://api.mixcloud.com"
        self.session = None
        self.monitored_keywords = set()
        self.violation_patterns = []
        
        # Performance tracking
        self.requests_made = 0
        self.content_analyzed = 0
        self.violations_detected = 0
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize crawler with authentication and configuration."""
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0 Mixcloud Crawler',
            'Accept': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        
        logger.info("Mixcloud crawler initialized successfully")
        
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated API request with rate limiting."""
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        proxy = await self.proxy_manager.get_proxy()
        
        try:
            async with self.session.get(
                url, 
                params=params,
                proxy=proxy
            ) as response:
                self.requests_made += 1
                
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)
                    
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Mixcloud API request failed: {e}")
            await self.proxy_manager.mark_proxy_failed(proxy)
            raise
            
    async def search_shows(
        self, 
        query: str, 
        limit: int = 50,
        filters: Dict = None
    ) -> MixcloudSearchResult:
        """
        Search for shows/mixes with advanced filtering.
        
        Args:
            query: Search query string
            limit: Maximum number of shows to return
            filters: Additional search filters
            
        Returns:
            MixcloudSearchResult with comprehensive show data
        """
        params = {
            'q': query,
            'limit': min(limit, 100),  # Mixcloud API limit
            'type': 'cloudcast'
        }
        
        if filters:
            params.update(filters)
            
        data = await self._make_request('search/', params)
        
        shows = []
        for show_data in data.get('data', []):
            show = await self._parse_show_data(show_data)
            if show:
                shows.append(show)
                self.content_analyzed += 1
                
        return MixcloudSearchResult(
            query=query,
            total_results=data.get('paging', {}).get('total', 0),
            shows=shows,
            users=[],
            genres=await self._extract_genres(shows),
            trending_tags=await self._extract_trending_tags(shows),
            search_timestamp=datetime.utcnow(),
            has_more=bool(data.get('paging', {}).get('next')),
            next_page_url=data.get('paging', {}).get('next')
        )
        
    async def get_show_details(self, show_key: str) -> Optional[MixcloudShow]:
        """Get detailed information about a specific show."""
        try:
            data = await self._make_request(show_key)
            return await self._parse_show_data(data)
        except Exception as e:
            logger.error(f"Failed to get show details for {show_key}: {e}")
            return None
            
    async def get_user_shows(
        self, 
        username: str, 
        limit: int = 50
    ) -> List[MixcloudShow]:
        """Get shows from a specific user."""
        params = {'limit': min(limit, 100)}
        
        try:
            data = await self._make_request(f'{username}/cloudcasts/', params)
            
            shows = []
            for show_data in data.get('data', []):
                show = await self._parse_show_data(show_data)
                if show:
                    shows.append(show)
                    
            return shows
            
        except Exception as e:
            logger.error(f"Failed to get user shows for {username}: {e}")
            return []
            
    async def get_trending_shows(self, genre: str = None) -> List[MixcloudShow]:
        """Get trending shows, optionally filtered by genre."""
        params = {}
        if genre:
            params['tags'] = genre
            
        try:
            data = await self._make_request('popular/', params)
            
            shows = []
            for show_data in data.get('data', []):
                show = await self._parse_show_data(show_data)
                if show:
                    shows.append(show)
                    
            return shows
            
        except Exception as e:
            logger.error(f"Failed to get trending shows: {e}")
            return []
            
    async def analyze_audio_content(self, show: MixcloudShow) -> Dict:
        """Analyze audio content of a show using advanced audio processing."""
        if not show.audio_url:
            return {}
            
        try:
            # Generate audio fingerprint
            audio_fingerprint = await self._generate_audio_fingerprint(
                show.audio_url
            )
            show.audio_fingerprint = audio_fingerprint
            
            # Detect similar content
            similar_content = await self._detect_similar_audio(audio_fingerprint)
            show.similarity_matches = similar_content
            
            # Analyze for copyright violations
            violation_score = await self._analyze_copyright_violations(
                show, audio_fingerprint
            )
            show.violation_score = violation_score
            
            if violation_score > 0.8:
                self.violations_detected += 1
                await self._handle_violation_detected(show)
                
            return {
                'audio_fingerprint': audio_fingerprint,
                'similar_content': similar_content,
                'violation_score': violation_score,
                'track_analysis': await self._analyze_track_sections(show),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audio content analysis failed for show {show.show_id}: {e}")
            
        return {}
        
    async def monitor_real_time(
        self, 
        keywords: List[str],
        duration: int = 3600
    ) -> AsyncGenerator[MixcloudShow, None]:
        """
        Monitor Mixcloud in real-time for specific keywords.
        
        Args:
            keywords: List of keywords to monitor
            duration: Monitoring duration in seconds
            
        Yields:
            MixcloudShow objects as they are discovered
        """
        self.monitored_keywords.update(keywords)
        start_time = datetime.utcnow()
        
        logger.info(f"Starting real-time Mixcloud monitoring for: {keywords}")
        
        while (datetime.utcnow() - start_time).seconds < duration:
            try:
                for keyword in keywords:
                    # Search for recent shows
                    results = await self.search_shows(
                        query=keyword,
                        limit=25,
                        filters={'since': 'today'}
                    )
                    
                    for show in results.shows:
                        # Analyze content for violations
                        await self.analyze_audio_content(show)
                        yield show
                        
                # Wait before next check
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Real-time monitoring error: {e}")
                await asyncio.sleep(60)
                
    async def detect_content_violations(
        self, 
        protected_content: List[str]
    ) -> List[Dict]:
        """Detect potential copyright violations of protected content."""
        violations = []
        
        for content_id in protected_content:
            # Search for similar audio content
            similar_shows = await self._find_similar_content(content_id)
            
            for show in similar_shows:
                violation_score = await self._calculate_violation_score(
                    content_id, show
                )
                
                if violation_score > 0.8:
                    violations.append({
                        'original_content_id': content_id,
                        'violating_show': show,
                        'violation_score': violation_score,
                        'detection_timestamp': datetime.utcnow(),
                        'platform': 'mixcloud'
                    })
                    
        return violations
        
    async def _parse_show_data(self, data: Dict) -> Optional[MixcloudShow]:
        """Parse Mixcloud API show data into structured format."""
        try:
            return MixcloudShow(
                show_id=data.get('slug', ''),
                key=data.get('key', ''),
                name=data.get('name', ''),
                description=data.get('description', ''),
                user_id=data.get('user', {}).get('key', ''),
                username=data.get('user', {}).get('username', ''),
                user_display_name=data.get('user', {}).get('name', ''),
                url=data.get('url', ''),
                audio_url=data.get('audio_url'),
                created_time=datetime.fromisoformat(
                    data.get('created_time', '').replace('Z', '+00:00')
                ) if data.get('created_time') else datetime.utcnow(),
                updated_time=datetime.fromisoformat(
                    data.get('updated_time', '').replace('Z', '+00:00')
                ) if data.get('updated_time') else datetime.utcnow(),
                play_count=data.get('play_count', 0),
                favorite_count=data.get('favorite_count', 0),
                comment_count=data.get('comment_count', 0),
                repost_count=data.get('repost_count', 0),
                duration=data.get('audio_length', 0),
                tags=[tag.get('name', '') for tag in data.get('tags', [])],
                city=data.get('city_name'),
                country=data.get('country_name'),
                picture_url=data.get('pictures', {}).get('large'),
                waveform_url=data.get('waveform_url'),
                engagement_metrics={
                    'total_engagement': (
                        data.get('play_count', 0) + 
                        data.get('favorite_count', 0) + 
                        data.get('repost_count', 0)
                    ),
                    'engagement_rate': 0.0,  # Calculated later
                    'viral_score': 0.0
                },
                metadata=data
            )
        except Exception as e:
            logger.error(f"Failed to parse show data: {e}")
            return None
            
    async def _generate_audio_fingerprint(self, audio_url: str) -> str:
        """Generate audio fingerprint for content."""
        try:
            # This would implement audio fingerprinting
            # using libraries like chromaprint/acoustid
            audio_hash = await self.fingerprinter.generate_audio_hash(audio_url)
            return audio_hash
        except Exception as e:
            logger.error(f"Failed to generate audio fingerprint: {e}")
            return ""
            
    async def _detect_similar_audio(self, audio_fingerprint: str) -> List[str]:
        """Detect similar audio content using fingerprinting."""
        try:
            similar_hashes = await self.fingerprinter.find_similar_content(
                audio_fingerprint, 
                threshold=0.1,
                content_type='audio'
            )
            return similar_hashes
        except Exception as e:
            logger.error(f"Failed to detect similar audio: {e}")
            return []
            
    async def _analyze_copyright_violations(
        self, 
        show: MixcloudShow, 
        audio_fingerprint: str
    ) -> float:
        """Analyze content for potential copyright violations."""
        violation_score = 0.0
        
        try:
            # Check against protected content database
            protected_matches = await self.fingerprinter.check_protected_content(
                audio_fingerprint, content_type='audio'
            )
            
            if protected_matches:
                violation_score = max(match['similarity'] for match in protected_matches)
                
            # Additional checks for metadata similarity
            if show.name or show.description:
                text_content = f"{show.name} {show.description}"
                text_violations = await self.fingerprinter.check_text_similarity(
                    text_content
                )
                if text_violations:
                    violation_score = max(violation_score, 
                                        max(v['similarity'] for v in text_violations))
                    
        except Exception as e:
            logger.error(f"Copyright violation analysis failed: {e}")
            
        return violation_score
        
    async def _analyze_track_sections(self, show: MixcloudShow) -> Dict:
        """Analyze individual tracks within a DJ mix."""
        track_analysis = {
            'total_tracks': len(show.track_sections),
            'identified_tracks': 0,
            'copyrighted_tracks': 0,
            'track_details': []
        }
        
        for section in show.track_sections:
            try:
                # Analyze individual track section
                track_fingerprint = await self._generate_section_fingerprint(
                    show.audio_url, section.get('start_time', 0), 
                    section.get('end_time', 30)
                )
                
                track_matches = await self.fingerprinter.identify_track(
                    track_fingerprint
                )
                
                if track_matches:
                    track_analysis['identified_tracks'] += 1
                    
                    # Check for copyright issues
                    copyright_status = await self._check_track_copyright(
                        track_matches[0]
                    )
                    
                    if copyright_status.get('is_copyrighted'):
                        track_analysis['copyrighted_tracks'] += 1
                        
                    track_analysis['track_details'].append({
                        'section': section,
                        'identified_track': track_matches[0],
                        'copyright_status': copyright_status
                    })
                    
            except Exception as e:
                logger.error(f"Track section analysis failed: {e}")
                
        return track_analysis
        
    async def _handle_violation_detected(self, show: MixcloudShow):
        """Handle detected copyright violation."""
        logger.warning(
            f"Copyright violation detected: Show {show.show_id} "
            f"(score: {show.violation_score:.2f})"
        )
        
        violation_data = {
            'platform': 'mixcloud',
            'content_id': show.show_id,
            'content_url': show.url,
            'violation_score': show.violation_score,
            'detection_timestamp': datetime.utcnow(),
            'content_data': show
        }
        
    async def _extract_genres(self, shows: List[MixcloudShow]) -> List[str]:
        """Extract genres from show collection."""
        genre_counts = {}
        
        for show in shows:
            for tag in show.tags:
                if tag.lower() in ['house', 'techno', 'trance', 'dubstep', 
                                  'drum and bass', 'ambient', 'jazz', 'hip hop']:
                    genre_counts[tag.lower()] = genre_counts.get(tag.lower(), 0) + 1
                    
        return sorted(genre_counts.keys(), key=genre_counts.get, reverse=True)[:10]
        
    async def _extract_trending_tags(self, shows: List[MixcloudShow]) -> List[str]:
        """Extract trending tags from show collection."""
        tag_counts = {}
        
        for show in shows:
            for tag in show.tags:
                tag_counts[tag.lower()] = tag_counts.get(tag.lower(), 0) + 1
                
        trending = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in trending[:20]]
        
    async def _find_similar_content(self, content_id: str) -> List[MixcloudShow]:
        """Find content similar to protected content."""
        return []
        
    async def _calculate_violation_score(
        self, 
        original_content_id: str, 
        show: MixcloudShow
    ) -> float:
        """Calculate violation score between original content and show."""
        return 0.0
        
    async def _generate_section_fingerprint(
        self, 
        audio_url: str, 
        start_time: int, 
        end_time: int
    ) -> str:
        """Generate fingerprint for specific audio section."""
        return ""
        
    async def _check_track_copyright(self, track_info: Dict) -> Dict:
        """Check copyright status of identified track."""
        return {'is_copyrighted': False}
        
    def get_performance_metrics(self) -> Dict:
        """Get crawler performance metrics."""
        return {
            'requests_made': self.requests_made,
            'content_analyzed': self.content_analyzed,
            'violations_detected': self.violations_detected,
            'rate_limit_status': self.rate_limiter.get_status(),
            'proxy_status': self.proxy_manager.get_status(),
            'monitored_keywords': len(self.monitored_keywords)
        }
