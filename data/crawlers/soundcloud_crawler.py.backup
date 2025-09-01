"""SoundCloud Crawler Implementation
=================================

Advanced SoundCloud audio platform crawler for music content discovery.
Implements comprehensive audio fingerprinting and music trend analysis.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re
import librosa
import numpy as np
from scipy.signal import find_peaks
import hashlib

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class SoundCloudTrack:
    """SoundCloud track information"""
    track_id: str
    title: str
    description: str
    permalink_url: str
    stream_url: str
    download_url: Optional[str]
    user_id: str
    username: str
    user_permalink_url: str
    artwork_url: Optional[str]
    waveform_url: Optional[str]
    created_at: datetime
    duration: int  # milliseconds
    playback_count: int
    like_count: int
    repost_count: int
    comment_count: int
    download_count: int
    genre: Optional[str]
    tag_list: List[str]
    bpm: Optional[float]
    key_signature: Optional[str]
    is_downloadable: bool
    is_streamable: bool
    is_public: bool
    license: str
    track_type: str  # original, remix, live, demo, etc.
    release_date: Optional[datetime]
    label_name: Optional[str]
    purchase_url: Optional[str]
    purchase_title: Optional[str]
    video_url: Optional[str]
    sharing: str  # public, private
    embeddable_by: str  # all, me, none
    monetization_model: str
    policy: str
    track_format: Dict[str, str]  # Format information
    audio_fingerprint: Optional[Dict[str, Any]]
    spectral_features: Optional[Dict[str, Any]]
    collaborative_tracks: List[str]


@dataclass
class SoundCloudUser:
    """SoundCloud user/artist information"""
    user_id: str
    username: str
    permalink: str
    permalink_url: str
    uri: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    city: Optional[str]
    country: Optional[str]
    description: Optional[str]
    discogs_name: Optional[str]
    myspace_name: Optional[str]
    website: Optional[str]
    website_title: Optional[str]
    online: bool
    track_count: int
    playlist_count: int
    public_favorites_count: int
    followers_count: int
    followings_count: int
    likes_count: int
    reposts_count: int
    comments_count: int
    avatar_url: Optional[str]
    banner_url: Optional[str]
    created_at: datetime
    last_modified: datetime
    plan: str  # Free, Pro, Pro Unlimited
    subscriptions: List[Dict[str, Any]]
    upload_seconds_used: int
    upload_seconds_left: int
    quota: Dict[str, int]
    private_tracks_count: int
    private_playlists_count: int
    primary_email_confirmed: bool
    locale: str
    mobile_networks: List[Dict[str, Any]]
    recent_tracks: List[SoundCloudTrack]
    popular_tracks: List[SoundCloudTrack]
    collaboration_networks: List[str]
    verified: bool
    pro_unlimited: bool
    is_monetization_enabled: bool


@dataclass
class SoundCloudPlaylist:
    """SoundCloud playlist information"""
    playlist_id: str
    title: str
    description: Optional[str]
    permalink_url: str
    user_id: str
    username: str
    user_permalink_url: str
    artwork_url: Optional[str]
    created_at: datetime
    duration: int  # Total duration in milliseconds
    track_count: int
    likes_count: int
    reposts_count: int
    sharing: str  # public, private
    embeddable_by: str
    purchase_url: Optional[str]
    purchase_title: Optional[str]
    label_name: Optional[str]
    label_id: Optional[str]
    release_day: Optional[int]
    release_month: Optional[int]
    release_year: Optional[int]
    streamable: bool
    downloadable: bool
    genre: Optional[str]
    tag_list: List[str]
    tracks: List[SoundCloudTrack]
    secret_token: Optional[str]
    secret_uri: Optional[str]
    last_modified: datetime
    playlist_type: str  # compilation, ep, single, album
    is_album: bool
    published_at: Optional[datetime]
    display_date: datetime


@dataclass
class SoundCloudComment:
    """SoundCloud comment information"""
    comment_id: str
    user_id: str
    username: str
    user_avatar_url: Optional[str]
    track_id: str
    created_at: datetime
    body: str
    timestamp: Optional[int]  # Position in track (milliseconds)
    uri: str
    self_uri: str


class SoundCloudCrawler(PlatformCrawler):
    """
    Advanced SoundCloud crawler for audio content monitoring and discovery.
    
    Features:
    - Track discovery and metadata extraction
    - Audio fingerprinting and analysis
    - User/artist profile monitoring
    - Playlist and album tracking
    - Comment and engagement analysis
    - Genre and tag trend detection
    - Music collaboration network mapping
    - Audio quality assessment
    - Copyright detection
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, client_id: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "soundcloud"
        self.base_url = "https://soundcloud.com"
        self.api_base_url = "https://api.soundcloud.com"
        self.api_v2_base_url = "https://api-v2.soundcloud.com"
        
        # SoundCloud API credentials
        self.client_id = client_id
        
        # Rate limiting (SoundCloud is moderate)
        self.requests_per_minute = 60
        self.min_delay = 1.0
        self.max_delay = 3.0
        
        # Content type mappings
        self.content_types = {
            'tracks': self._crawl_tracks,
            'users': self._crawl_users,
            'playlists': self._crawl_playlists,
            'search': self._crawl_search,
            'trending': self._crawl_trending,
            'genres': self._crawl_genres,
            'tags': self._crawl_tags
        }
        
        # Audio analysis tools
        self.audio_sample_rate = 22050
        self.audio_duration_limit = 30  # seconds for fingerprinting
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup SoundCloud-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://soundcloud.com',
            'Referer': 'https://soundcloud.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "tracks", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """
        Search for content on SoundCloud.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} SoundCloud {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching SoundCloud content: {str(e)}")
            return []
    
    async def _crawl_tracks(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl SoundCloud tracks"""
        try:
            results = []
            
            # Search for tracks
            params = {
                'q': query,
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_base_url}/tracks"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for track_data in data.get('collection', []):
                        # Parse track data
                        track = await self._parse_track_data(track_data)
                        if track:
                            # Get audio fingerprint if streamable
                            if track.is_streamable and track.stream_url:
                                fingerprint = await self._extract_audio_fingerprint(track.stream_url)
                                track.audio_fingerprint = fingerprint
                            
                            result = CrawlerResult(
                                url=track.permalink_url,
                                title=track.title,
                                content=f"Track by {track.username}: {track.description}",
                                metadata={
                                    'track_data': asdict(track),
                                    'platform': 'soundcloud',
                                    'content_type': 'track',
                                    'duration': track.duration,
                                    'playback_count': track.playback_count,
                                    'like_count': track.like_count,
                                    'genre': track.genre,
                                    'tag_list': track.tag_list,
                                    'audio_fingerprint': track.audio_fingerprint
                                },
                                timestamp=track.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching tracks: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud tracks: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl SoundCloud users"""
        try:
            results = []
            
            # Search for users
            params = {
                'q': query,
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_base_url}/users"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for user_data in data.get('collection', []):
                        # Get detailed user information
                        detailed_user = await self._get_detailed_user_info(user_data['id'])
                        if detailed_user:
                            result = CrawlerResult(
                                url=detailed_user.permalink_url,
                                title=detailed_user.username,
                                content=f"Artist: {detailed_user.full_name or detailed_user.username} - {detailed_user.description}",
                                metadata={
                                    'user_data': asdict(detailed_user),
                                    'platform': 'soundcloud',
                                    'content_type': 'user',
                                    'track_count': detailed_user.track_count,
                                    'followers_count': detailed_user.followers_count,
                                    'likes_count': detailed_user.likes_count,
                                    'plan': detailed_user.plan,
                                    'verified': detailed_user.verified
                                },
                                timestamp=detailed_user.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching users: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud users: {str(e)}")
            return []
    
    async def _crawl_playlists(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl SoundCloud playlists"""
        try:
            results = []
            
            # Search for playlists
            params = {
                'q': query,
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_base_url}/playlists"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for playlist_data in data.get('collection', []):
                        # Parse playlist data
                        playlist = await self._parse_playlist_data(playlist_data)
                        if playlist:
                            result = CrawlerResult(
                                url=playlist.permalink_url,
                                title=playlist.title,
                                content=f"Playlist by {playlist.username}: {playlist.description}",
                                metadata={
                                    'playlist_data': asdict(playlist),
                                    'platform': 'soundcloud',
                                    'content_type': 'playlist',
                                    'track_count': playlist.track_count,
                                    'duration': playlist.duration,
                                    'likes_count': playlist.likes_count,
                                    'genre': playlist.genre,
                                    'playlist_type': playlist.playlist_type
                                },
                                timestamp=playlist.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching playlists: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud playlists: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General SoundCloud search"""
        try:
            results = []
            
            # Search across different content types
            tracks = await self._crawl_tracks(query, max_results // 3)
            users = await self._crawl_users(query, max_results // 3)
            playlists = await self._crawl_playlists(query, max_results // 3)
            
            results.extend(tracks)
            results.extend(users)
            results.extend(playlists)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing SoundCloud search: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl trending content"""
        try:
            results = []
            
            # Get trending tracks (SoundCloud's "Hot & New")
            params = {
                'genre': 'soundcloud:genres:all-music',
                'kind': 'trending',
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_v2_base_url}/charts"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for track_data in data.get('collection', []):
                        if 'track' in track_data:
                            track = await self._parse_track_data(track_data['track'])
                            if track and (not query or query.lower() in track.title.lower()):
                                result = CrawlerResult(
                                    url=track.permalink_url,
                                    title=f"[TRENDING] {track.title}",
                                    content=f"Trending track by {track.username}: {track.description}",
                                    metadata={
                                        'track_data': asdict(track),
                                        'platform': 'soundcloud',
                                        'content_type': 'trending_track',
                                        'trend_position': len(results) + 1,
                                        'playback_count': track.playback_count,
                                        'like_count': track.like_count
                                    },
                                    timestamp=track.created_at,
                                    similarity_score=0.0
                                )
                                results.append(result)
                
                else:
                    self.logger.error(f"Error fetching trending content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud trending: {str(e)}")
            return []
    
    async def _crawl_genres(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl content by genre"""
        try:
            results = []
            
            # Get tracks by genre
            params = {
                'genres': query,
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_base_url}/tracks"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for track_data in data.get('collection', []):
                        track = await self._parse_track_data(track_data)
                        if track:
                            result = CrawlerResult(
                                url=track.permalink_url,
                                title=f"[{query.upper()}] {track.title}",
                                content=f"Genre track by {track.username}: {track.description}",
                                metadata={
                                    'track_data': asdict(track),
                                    'platform': 'soundcloud',
                                    'content_type': 'genre_track',
                                    'genre': track.genre,
                                    'search_genre': query
                                },
                                timestamp=track.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching genre content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud genres: {str(e)}")
            return []
    
    async def _crawl_tags(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl content by tags"""
        try:
            results = []
            
            # Get tracks by tag
            params = {
                'tags': query,
                'client_id': self.client_id,
                'limit': min(max_results, 200),
                'offset': 0,
                'linked_partitioning': 1
            }
            
            api_url = f"{self.api_base_url}/tracks"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for track_data in data.get('collection', []):
                        track = await self._parse_track_data(track_data)
                        if track and query in track.tag_list:
                            result = CrawlerResult(
                                url=track.permalink_url,
                                title=f"[#{query}] {track.title}",
                                content=f"Tagged track by {track.username}: {track.description}",
                                metadata={
                                    'track_data': asdict(track),
                                    'platform': 'soundcloud',
                                    'content_type': 'tagged_track',
                                    'tag_list': track.tag_list,
                                    'search_tag': query
                                },
                                timestamp=track.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching tagged content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud tags: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_track_data(self, track_data: Dict[str, Any]) -> Optional[SoundCloudTrack]:
        """Parse track data from API response"""
        try:
            created_at = datetime.fromisoformat(track_data.get('created_at', '').replace('Z', '+00:00'))
            
            # Parse user information
            user_data = track_data.get('user', {})
            
            # Parse tag list
            tag_list = []
            if track_data.get('tag_list'):
                tag_list = [tag.strip() for tag in track_data['tag_list'].split()]
            
            # Parse stream URL
            stream_url = None
            if track_data.get('streamable') and self.client_id:
                stream_url = f"{track_data.get('stream_url', '')}?client_id={self.client_id}"
            
            track = SoundCloudTrack(
                track_id=str(track_data.get('id', '')),
                title=track_data.get('title', ''),
                description=track_data.get('description', '') or '',
                permalink_url=track_data.get('permalink_url', ''),
                stream_url=stream_url,
                download_url=track_data.get('download_url'),
                user_id=str(user_data.get('id', '')),
                username=user_data.get('username', ''),
                user_permalink_url=user_data.get('permalink_url', ''),
                artwork_url=track_data.get('artwork_url'),
                waveform_url=track_data.get('waveform_url'),
                created_at=created_at,
                duration=track_data.get('duration', 0),
                playback_count=track_data.get('playback_count', 0),
                like_count=track_data.get('likes_count', 0),
                repost_count=track_data.get('reposts_count', 0),
                comment_count=track_data.get('comment_count', 0),
                download_count=track_data.get('download_count', 0),
                genre=track_data.get('genre'),
                tag_list=tag_list,
                bpm=track_data.get('bpm'),
                key_signature=track_data.get('key_signature'),
                is_downloadable=track_data.get('downloadable', False),
                is_streamable=track_data.get('streamable', False),
                is_public=track_data.get('public', True),
                license=track_data.get('license', 'all-rights-reserved'),
                track_type=track_data.get('track_type', 'original'),
                release_date=None,  # Would need additional parsing
                label_name=track_data.get('label_name'),
                purchase_url=track_data.get('purchase_url'),
                purchase_title=track_data.get('purchase_title'),
                video_url=track_data.get('video_url'),
                sharing=track_data.get('sharing', 'public'),
                embeddable_by=track_data.get('embeddable_by', 'all'),
                monetization_model=track_data.get('monetization_model', 'NOT_APPLICABLE'),
                policy=track_data.get('policy', 'ALLOW'),
                track_format=track_data.get('format', {}),
                audio_fingerprint=None,  # Will be filled later
                spectral_features=None,  # Will be filled later
                collaborative_tracks=[]
            )
            
            return track
            
        except Exception as e:
            self.logger.error(f"Error parsing track data: {str(e)}")
            return None
    
    async def _parse_playlist_data(self, playlist_data: Dict[str, Any]) -> Optional[SoundCloudPlaylist]:
        """Parse playlist data from API response"""
        try:
            created_at = datetime.fromisoformat(playlist_data.get('created_at', '').replace('Z', '+00:00'))
            last_modified = datetime.fromisoformat(playlist_data.get('last_modified', '').replace('Z', '+00:00'))
            
            # Parse user information
            user_data = playlist_data.get('user', {})
            
            # Parse tracks
            tracks = []
            for track_data in playlist_data.get('tracks', []):
                track = await self._parse_track_data(track_data)
                if track:
                    tracks.append(track)
            
            # Parse tag list
            tag_list = []
            if playlist_data.get('tag_list'):
                tag_list = [tag.strip() for tag in playlist_data['tag_list'].split()]
            
            playlist = SoundCloudPlaylist(
                playlist_id=str(playlist_data.get('id', '')),
                title=playlist_data.get('title', ''),
                description=playlist_data.get('description'),
                permalink_url=playlist_data.get('permalink_url', ''),
                user_id=str(user_data.get('id', '')),
                username=user_data.get('username', ''),
                user_permalink_url=user_data.get('permalink_url', ''),
                artwork_url=playlist_data.get('artwork_url'),
                created_at=created_at,
                duration=playlist_data.get('duration', 0),
                track_count=playlist_data.get('track_count', len(tracks)),
                likes_count=playlist_data.get('likes_count', 0),
                reposts_count=playlist_data.get('reposts_count', 0),
                sharing=playlist_data.get('sharing', 'public'),
                embeddable_by=playlist_data.get('embeddable_by', 'all'),
                purchase_url=playlist_data.get('purchase_url'),
                purchase_title=playlist_data.get('purchase_title'),
                label_name=playlist_data.get('label_name'),
                label_id=playlist_data.get('label_id'),
                release_day=playlist_data.get('release_day'),
                release_month=playlist_data.get('release_month'),
                release_year=playlist_data.get('release_year'),
                streamable=playlist_data.get('streamable', True),
                downloadable=playlist_data.get('downloadable', False),
                genre=playlist_data.get('genre'),
                tag_list=tag_list,
                tracks=tracks,
                secret_token=playlist_data.get('secret_token'),
                secret_uri=playlist_data.get('secret_uri'),
                last_modified=last_modified,
                playlist_type=playlist_data.get('playlist_type', 'playlist'),
                is_album=playlist_data.get('is_album', False),
                published_at=None,  # Would need additional parsing
                display_date=created_at
            )
            
            return playlist
            
        except Exception as e:
            self.logger.error(f"Error parsing playlist data: {str(e)}")
            return None
    
    async def _get_detailed_user_info(self, user_id: str) -> Optional[SoundCloudUser]:
        """Get detailed user information"""
        try:
            api_url = f"{self.api_base_url}/users/{user_id}"
            params = {'client_id': self.client_id}
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return await self._parse_user_data(user_data)
                
        except Exception as e:
            self.logger.error(f"Error getting detailed user info: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[SoundCloudUser]:
        """Parse user data from API response"""
        try:
            created_at = datetime.fromisoformat(user_data.get('created_at', '').replace('Z', '+00:00'))
            last_modified = datetime.fromisoformat(user_data.get('last_modified', '').replace('Z', '+00:00'))
            
            user = SoundCloudUser(
                user_id=str(user_data.get('id', '')),
                username=user_data.get('username', ''),
                permalink=user_data.get('permalink', ''),
                permalink_url=user_data.get('permalink_url', ''),
                uri=user_data.get('uri', ''),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                full_name=user_data.get('full_name'),
                city=user_data.get('city'),
                country=user_data.get('country'),
                description=user_data.get('description'),
                discogs_name=user_data.get('discogs_name'),
                myspace_name=user_data.get('myspace_name'),
                website=user_data.get('website'),
                website_title=user_data.get('website_title'),
                online=user_data.get('online', False),
                track_count=user_data.get('track_count', 0),
                playlist_count=user_data.get('playlist_count', 0),
                public_favorites_count=user_data.get('public_favorites_count', 0),
                followers_count=user_data.get('followers_count', 0),
                followings_count=user_data.get('followings_count', 0),
                likes_count=user_data.get('likes_count', 0),
                reposts_count=user_data.get('reposts_count', 0),
                comments_count=user_data.get('comments_count', 0),
                avatar_url=user_data.get('avatar_url'),
                banner_url=user_data.get('banner_url'),
                created_at=created_at,
                last_modified=last_modified,
                plan=user_data.get('plan', 'Free'),
                subscriptions=user_data.get('subscriptions', []),
                upload_seconds_used=user_data.get('upload_seconds_used', 0),
                upload_seconds_left=user_data.get('upload_seconds_left', 0),
                quota=user_data.get('quota', {}),
                private_tracks_count=user_data.get('private_tracks_count', 0),
                private_playlists_count=user_data.get('private_playlists_count', 0),
                primary_email_confirmed=user_data.get('primary_email_confirmed', False),
                locale=user_data.get('locale', 'en'),
                mobile_networks=user_data.get('mobile_networks', []),
                recent_tracks=[],  # Would need additional API calls
                popular_tracks=[],  # Would need additional API calls
                collaboration_networks=[],
                verified=user_data.get('verified', False),
                pro_unlimited=user_data.get('pro_unlimited', False),
                is_monetization_enabled=user_data.get('monetization_model') != 'NOT_APPLICABLE'
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _extract_audio_fingerprint(self, stream_url: str) -> Optional[Dict[str, Any]]:
        """Extract audio fingerprint from track"""
        try:
            # Download a sample of the audio
            async with self.session.get(stream_url) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Save temporarily for processing
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_file.write(audio_data)
                        temp_path = temp_file.name
                    
                    try:
                        # Load audio with librosa
                        y, sr = librosa.load(temp_path, sr=self.audio_sample_rate, duration=self.audio_duration_limit)
                        
                        # Extract features
                        fingerprint = {
                            'duration': len(y) / sr,
                            'sample_rate': sr,
                            'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
                            'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
                            'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(y)),
                            'mfcc': np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1).tolist(),
                            'chroma': np.mean(librosa.feature.chroma(y=y, sr=sr), axis=1).tolist(),
                            'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0]),
                            'spectral_contrast': np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1).tolist()
                        }
                        
                        # Create hash for similarity matching
                        fingerprint_str = json.dumps(fingerprint, sort_keys=True)
                        fingerprint['hash'] = hashlib.md5(fingerprint_str.encode()).hexdigest()
                        
                        return fingerprint
                        
                    finally:
                        # Clean up temporary file
                        os.unlink(temp_path)
                
        except Exception as e:
            self.logger.error(f"Error extracting audio fingerprint: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from SoundCloud content"""
        try:
            # Parse URL to determine content type
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'soundcloud',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            if len(path_parts) >= 2:
                username = path_parts[0]
                content_identifier = path_parts[1]
                
                if content_identifier == 'sets':
                    # Playlist URL
                    if len(path_parts) >= 3:
                        playlist_permalink = path_parts[2]
                        playlist_data = await self._get_playlist_by_permalink(username, playlist_permalink)
                        if playlist_data:
                            metadata.update({
                                'content_type': 'playlist',
                                'playlist_data': asdict(playlist_data)
                            })
                else:
                    # Track URL
                    track_data = await self._get_track_by_permalink(username, content_identifier)
                    if track_data:
                        metadata.update({
                            'content_type': 'track',
                            'track_data': asdict(track_data)
                        })
            
            elif len(path_parts) == 1:
                # User profile URL
                username = path_parts[0]
                user_data = await self._get_user_by_permalink(username)
                if user_data:
                    metadata.update({
                        'content_type': 'user',
                        'user_data': asdict(user_data)
                    })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting SoundCloud metadata: {str(e)}")
            return {'error': str(e)}
    
    async def _get_track_by_permalink(self, username: str, track_permalink: str) -> Optional[SoundCloudTrack]:
        """Get track by permalink"""
        try:
            track_url = f"{self.base_url}/{username}/{track_permalink}"
            
            # Resolve URL to get track ID
            resolve_params = {
                'url': track_url,
                'client_id': self.client_id
            }
            
            async with self.session.get(
                f"{self.api_base_url}/resolve",
                params=resolve_params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    track_data = await response.json()
                    return await self._parse_track_data(track_data)
                
        except Exception as e:
            self.logger.error(f"Error getting track by permalink: {str(e)}")
            return None
    
    async def _get_playlist_by_permalink(self, username: str, playlist_permalink: str) -> Optional[SoundCloudPlaylist]:
        """Get playlist by permalink"""
        try:
            playlist_url = f"{self.base_url}/{username}/sets/{playlist_permalink}"
            
            # Resolve URL to get playlist ID
            resolve_params = {
                'url': playlist_url,
                'client_id': self.client_id
            }
            
            async with self.session.get(
                f"{self.api_base_url}/resolve",
                params=resolve_params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    playlist_data = await response.json()
                    return await self._parse_playlist_data(playlist_data)
                
        except Exception as e:
            self.logger.error(f"Error getting playlist by permalink: {str(e)}")
            return None
    
    async def _get_user_by_permalink(self, username: str) -> Optional[SoundCloudUser]:
        """Get user by permalink"""
        try:
            user_url = f"{self.base_url}/{username}"
            
            # Resolve URL to get user ID
            resolve_params = {
                'url': user_url,
                'client_id': self.client_id
            }
            
            async with self.session.get(
                f"{self.api_base_url}/resolve",
                params=resolve_params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return await self._parse_user_data(user_data)
                
        except Exception as e:
            self.logger.error(f"Error getting user by permalink: {str(e)}")
            return None
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get SoundCloud platform information"""
        return {
            'platform_name': 'SoundCloud',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Track discovery and metadata extraction',
                'Audio fingerprinting and analysis',
                'User/artist profile monitoring',
                'Playlist and album tracking',
                'Comment and engagement analysis',
                'Genre and tag trend detection',
                'Music collaboration network mapping',
                'Audio quality assessment',
                'Copyright detection'
            ],
            'audio_analysis': {
                'sample_rate': self.audio_sample_rate,
                'fingerprint_duration_limit': self.audio_duration_limit,
                'supported_features': [
                    'MFCC', 'Chroma', 'Spectral Centroid',
                    'Spectral Rolloff', 'Zero Crossing Rate',
                    'Tempo', 'Spectral Contrast'
                ]
            },
            'authentication': {
                'required': True,
                'type': 'Client ID',
                'scope': 'Read-only access'
            }
        }
