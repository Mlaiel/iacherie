"""Bandcamp Crawler Implementation
===============================

Advanced Bandcamp platform crawler for independent music monitoring.
Implements comprehensive Track, Album, Artist, and Label tracking.

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
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re
from bs4 import BeautifulSoup

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class BandcampTrack:
    """Bandcamp track information"""
    track_id: str
    title: str
    artist_name: str
    artist_url: str
    album_title: str
    album_url: str
    duration: int  # seconds
    track_number: int
    price: Optional[float]
    currency: str
    streaming_url: Optional[str]
    download_url: Optional[str]
    lyrics: Optional[str]
    credits: str
    about: str
    tags: List[str]
    release_date: datetime
    license_type: str
    is_downloadable: bool
    is_streamable: bool
    play_count: int
    favorite_count: int
    comment_count: int
    purchase_count: int
    artwork_url: str
    file_formats: List[str]
    min_price: Optional[float]
    suggested_price: Optional[float]
    location: Optional[str]
    label: Optional[str]


@dataclass
class BandcampAlbum:
    """Bandcamp album information"""
    album_id: str
    title: str
    artist_name: str
    artist_url: str
    url: str
    description: str
    release_date: datetime
    tags: List[str]
    track_count: int
    tracks: List[str]  # Track IDs
    price: Optional[float]
    currency: str
    min_price: Optional[float]
    suggested_price: Optional[float]
    is_preorder: bool
    release_type: str  # album, EP, single, compilation
    artwork_url: str
    credits: str
    license_type: str
    is_downloadable: bool
    is_streamable: bool
    purchase_count: int
    favorite_count: int
    comment_count: int
    wishlist_count: int
    supported_by_count: int
    location: Optional[str]
    label: Optional[str]
    catalog_number: Optional[str]
    upc: Optional[str]


@dataclass
class BandcampArtist:
    """Bandcamp artist information"""
    artist_id: str
    name: str
    url: str
    bio: str
    location: Optional[str]
    website: Optional[str]
    facebook_url: Optional[str]
    twitter_url: Optional[str]
    instagram_url: Optional[str]
    youtube_url: Optional[str]
    spotify_url: Optional[str]
    bandcamp_url: str
    image_url: str
    banner_url: Optional[str]
    follower_count: int
    following_count: int
    album_count: int
    track_count: int
    wishlist_count: int
    collection_count: int
    genres: List[str]
    labels: List[str]
    discography: List[str]  # Album IDs
    featured_track: Optional[str]
    is_label: bool
    is_verified: bool
    signup_date: Optional[datetime]
    last_active: Optional[datetime]


@dataclass
class BandcampLabel:
    """Bandcamp label information"""
    label_id: str
    name: str
    url: str
    description: str
    location: Optional[str]
    website: Optional[str]
    contact_email: Optional[str]
    image_url: str
    banner_url: Optional[str]
    artist_count: int
    release_count: int
    follower_count: int
    artists: List[str]  # Artist IDs
    releases: List[str]  # Album IDs
    genres: List[str]
    featured_release: Optional[str]
    established_date: Optional[datetime]
    social_links: Dict[str, str]


@dataclass
class BandcampFan:
    """Bandcamp fan information"""
    fan_id: str
    username: str
    display_name: str
    url: str
    bio: Optional[str]
    location: Optional[str]
    image_url: str
    following_count: int
    follower_count: int
    collection_count: int
    wishlist_count: int
    collection: List[str]  # Album IDs
    wishlist: List[str]  # Album IDs
    following_artists: List[str]
    following_labels: List[str]
    following_fans: List[str]
    genres: List[str]
    signup_date: Optional[datetime]
    last_active: Optional[datetime]


class BandcampCrawler(PlatformCrawler):
    """
    Advanced Bandcamp crawler for independent music monitoring.
    
    Features:
    - Track content tracking
    - Album monitoring
    - Artist profile analysis
    - Label tracking
    - Fan activity monitoring
    - Genre-based discovery
    - Sales and pricing analysis
    - Independent music discovery
    - Artist support tracking
    - Music collection analysis
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "bandcamp"
        self.base_url = "https://bandcamp.com"
        self.api_base_url = "https://bandcamp.com/api"
        
        # Rate limiting (Bandcamp is more lenient but we should be respectful)
        self.requests_per_minute = 30
        self.min_delay = 2.0
        self.max_delay = 4.0
        
        # Content type mappings
        self.content_types = {
            'tracks': self._crawl_tracks,
            'albums': self._crawl_albums,
            'artists': self._crawl_artists,
            'labels': self._crawl_labels,
            'fans': self._crawl_fans,
            'search': self._crawl_search,
            'discover': self._crawl_discover,
            'genres': self._crawl_genres
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Bandcamp-specific headers"""
        self.session_headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://bandcamp.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    async def search_content(self, query: str, content_type: str = "tracks", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on Bandcamp.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Bandcamp {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Bandcamp content: {str(e)}")
            return []
    
    async def _crawl_tracks(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp tracks"""
        try:
            results = []
            
            # Bandcamp search endpoint
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'item_type': 't',  # tracks
                'from': 'search'
            }
            
            # Apply filters
            if filters:
                if 'genre' in filters:
                    params['genre'] = filters['genre']
                if 'location' in filters:
                    params['location'] = filters['location']
                if 'format' in filters:
                    params['format'] = filters['format']
            
            # Mock data for demonstration
            mock_tracks = await self._get_mock_tracks(query, max_results)
            
            for track_data in mock_tracks:
                track = await self._parse_track_data(track_data)
                if track:
                    result = CrawlerResult(
                        url=f"{self.base_url}/track/{track.track_id}",
                        title=f"{track.title} - {track.artist_name}",
                        content=track.about,
                        metadata={
                            'track_data': asdict(track),
                            'platform': 'bandcamp',
                            'content_type': 'track',
                            'duration': track.duration,
                            'price': track.price,
                            'currency': track.currency,
                            'tags': track.tags,
                            'is_downloadable': track.is_downloadable,
                            'is_streamable': track.is_streamable,
                            'play_count': track.play_count,
                            'purchase_count': track.purchase_count,
                            'location': track.location,
                            'label': track.label
                        },
                        timestamp=track.release_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp tracks: {str(e)}")
            return []
    
    async def _crawl_albums(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp albums"""
        try:
            results = []
            
            # Bandcamp search endpoint
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'item_type': 'a',  # albums
                'from': 'search'
            }
            
            # Apply filters
            if filters:
                if 'genre' in filters:
                    params['genre'] = filters['genre']
                if 'location' in filters:
                    params['location'] = filters['location']
                if 'format' in filters:
                    params['format'] = filters['format']
            
            # Mock data
            mock_albums = await self._get_mock_albums(query, max_results)
            
            for album_data in mock_albums:
                album = await self._parse_album_data(album_data)
                if album:
                    result = CrawlerResult(
                        url=album.url,
                        title=f"{album.title} - {album.artist_name}",
                        content=album.description,
                        metadata={
                            'album_data': asdict(album),
                            'platform': 'bandcamp',
                            'content_type': 'album',
                            'track_count': album.track_count,
                            'price': album.price,
                            'currency': album.currency,
                            'release_type': album.release_type,
                            'tags': album.tags,
                            'is_downloadable': album.is_downloadable,
                            'purchase_count': album.purchase_count,
                            'supported_by_count': album.supported_by_count,
                            'location': album.location,
                            'label': album.label
                        },
                        timestamp=album.release_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp albums: {str(e)}")
            return []
    
    async def _crawl_artists(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp artists"""
        try:
            results = []
            
            # Bandcamp search endpoint
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'item_type': 'b',  # bands/artists
                'from': 'search'
            }
            
            # Mock data
            mock_artists = await self._get_mock_artists(query, max_results)
            
            for artist_data in mock_artists:
                artist = await self._parse_artist_data(artist_data)
                if artist:
                    result = CrawlerResult(
                        url=artist.url,
                        title=artist.name,
                        content=artist.bio,
                        metadata={
                            'artist_data': asdict(artist),
                            'platform': 'bandcamp',
                            'content_type': 'artist',
                            'follower_count': artist.follower_count,
                            'album_count': artist.album_count,
                            'track_count': artist.track_count,
                            'genres': artist.genres,
                            'is_label': artist.is_label,
                            'is_verified': artist.is_verified,
                            'location': artist.location,
                            'labels': artist.labels
                        },
                        timestamp=artist.signup_date or datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp artists: {str(e)}")
            return []
    
    async def _crawl_labels(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp labels"""
        try:
            results = []
            
            # Mock data for labels
            mock_labels = await self._get_mock_labels(query, max_results)
            
            for label_data in mock_labels:
                label = await self._parse_label_data(label_data)
                if label:
                    result = CrawlerResult(
                        url=label.url,
                        title=label.name,
                        content=label.description,
                        metadata={
                            'label_data': asdict(label),
                            'platform': 'bandcamp',
                            'content_type': 'label',
                            'artist_count': label.artist_count,
                            'release_count': label.release_count,
                            'follower_count': label.follower_count,
                            'genres': label.genres,
                            'location': label.location,
                            'social_links': label.social_links
                        },
                        timestamp=label.established_date or datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp labels: {str(e)}")
            return []
    
    async def _crawl_fans(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp fans"""
        try:
            results = []
            
            # Mock data for fans
            mock_fans = await self._get_mock_fans(query, max_results)
            
            for fan_data in mock_fans:
                fan = await self._parse_fan_data(fan_data)
                if fan:
                    result = CrawlerResult(
                        url=fan.url,
                        title=f"Fan: {fan.display_name} (@{fan.username})",
                        content=fan.bio or f"Bandcamp fan with {fan.collection_count} items in collection",
                        metadata={
                            'fan_data': asdict(fan),
                            'platform': 'bandcamp',
                            'content_type': 'fan',
                            'collection_count': fan.collection_count,
                            'wishlist_count': fan.wishlist_count,
                            'following_count': fan.following_count,
                            'follower_count': fan.follower_count,
                            'genres': fan.genres,
                            'location': fan.location
                        },
                        timestamp=fan.signup_date or datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp fans: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Bandcamp search"""
        try:
            results = []
            
            # Search across different content types
            tracks = await self._crawl_tracks(query, max_results // 3, filters)
            albums = await self._crawl_albums(query, max_results // 3, filters)
            artists = await self._crawl_artists(query, max_results // 3, filters)
            
            results.extend(tracks)
            results.extend(albums)
            results.extend(artists)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Bandcamp search: {str(e)}")
            return []
    
    async def _crawl_discover(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp discover page"""
        try:
            results = []
            
            # Get discover content
            discover_url = f"{self.base_url}/discover"
            discover_content = await self._get_discover_content(query, max_results, filters)
            
            for content in discover_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[DISCOVER] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'discover_data': content,
                        'platform': 'bandcamp',
                        'content_type': 'discover',
                        'featured': True,
                        'genre': content.get('genre'),
                        'location': content.get('location')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp discover: {str(e)}")
            return []
    
    async def _crawl_genres(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Bandcamp by genres"""
        try:
            results = []
            
            # Get genre-specific content
            genres = await self._get_genres()
            
            # Filter genres by query if provided
            if query:
                relevant_genres = [g for g in genres if query.lower() in g.lower()]
            else:
                relevant_genres = genres[:10]
            
            for genre in relevant_genres:
                genre_content = await self._get_genre_content(genre, max_results // len(relevant_genres))
                
                for content in genre_content:
                    result = CrawlerResult(
                        url=content.get('url', ''),
                        title=f"[{genre.upper()}] {content.get('title', 'Unknown')}",
                        content=content.get('description', ''),
                        metadata={
                            'content_data': content,
                            'platform': 'bandcamp',
                            'content_type': 'genre_content',
                            'genre': genre
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Bandcamp genres: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_tracks(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock track data"""
        tracks = []
        
        for i in range(min(max_results, 30)):
            tracks.append({
                'id': f'track_{i}',
                'title': f'{query} Track {i}' if query else f'Track {i}',
                'artist_name': f'{query} Artist {i}' if query else f'Artist {i}',
                'album_title': f'{query} Album {i}' if query else f'Album {i}',
                'duration': random.randint(120, 480),  # 2-8 minutes
                'track_number': i + 1,
                'price': random.choice([None, round(random.uniform(0.50, 3.00), 2)]),
                'currency': 'USD',
                'about': f'Independent track about {query}' if query else f'Track description {i}',
                'tags': [query] if query else ['indie', 'experimental', 'electronic'],
                'release_date': (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
                'license_type': random.choice(['all-rights-reserved', 'cc-by', 'cc-by-sa']),
                'is_downloadable': True,
                'is_streamable': True,
                'play_count': random.randint(10, 10000),
                'favorite_count': random.randint(0, 500),
                'purchase_count': random.randint(0, 100),
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK']),
                'label': f'{query} Records' if query else f'Label {i}'
            })
        
        return tracks
    
    async def _get_mock_albums(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock album data"""
        albums = []
        
        for i in range(min(max_results, 25)):
            albums.append({
                'id': f'album_{i}',
                'title': f'{query} Album {i}' if query else f'Album {i}',
                'artist_name': f'{query} Artist {i}' if query else f'Artist {i}',
                'url': f'https://artist{i}.bandcamp.com/album/{query.lower() if query else "album"}-{i}',
                'description': f'Independent album featuring {query}' if query else f'Album description {i}',
                'release_date': (datetime.utcnow() - timedelta(days=random.randint(30, 730))).isoformat(),
                'tags': [query] if query else ['indie', 'alternative', 'experimental'],
                'track_count': random.randint(6, 15),
                'price': random.choice([None, round(random.uniform(5.00, 15.00), 2)]),
                'currency': 'USD',
                'min_price': round(random.uniform(3.00, 8.00), 2),
                'release_type': random.choice(['album', 'EP', 'single', 'compilation']),
                'is_downloadable': True,
                'purchase_count': random.randint(5, 500),
                'supported_by_count': random.randint(10, 1000),
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK']),
                'label': f'{query} Records' if query else f'Label {i}'
            })
        
        return albums
    
    async def _get_mock_artists(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock artist data"""
        artists = []
        
        for i in range(min(max_results, 20)):
            artists.append({
                'id': f'artist_{i}',
                'name': f'{query} Artist {i}' if query else f'Artist {i}',
                'url': f'https://{query.lower() if query else "artist"}{i}.bandcamp.com',
                'bio': f'Independent artist creating {query} music' if query else f'Artist bio {i}',
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK']),
                'follower_count': random.randint(50, 5000),
                'album_count': random.randint(1, 10),
                'track_count': random.randint(5, 50),
                'genres': [query] if query else ['indie', 'experimental', 'electronic'],
                'is_label': random.choice([True, False]),
                'is_verified': random.choice([True, False]),
                'signup_date': (datetime.utcnow() - timedelta(days=random.randint(365, 2555))).isoformat()
            })
        
        return artists
    
    async def _get_mock_labels(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock label data"""
        labels = []
        
        for i in range(min(max_results, 15)):
            labels.append({
                'id': f'label_{i}',
                'name': f'{query} Records {i}' if query else f'Label {i}',
                'url': f'https://{query.lower() if query else "label"}{i}.bandcamp.com',
                'description': f'Independent label promoting {query} music' if query else f'Label description {i}',
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK']),
                'artist_count': random.randint(5, 50),
                'release_count': random.randint(10, 200),
                'follower_count': random.randint(100, 10000),
                'genres': [query] if query else ['indie', 'experimental', 'electronic'],
                'established_date': (datetime.utcnow() - timedelta(days=random.randint(1095, 7300))).isoformat()
            })
        
        return labels
    
    async def _get_mock_fans(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock fan data"""
        fans = []
        
        for i in range(min(max_results, 20)):
            fans.append({
                'id': f'fan_{i}',
                'username': f'{query.lower() if query else "fan"}{i}',
                'display_name': f'{query} Fan {i}' if query else f'Fan {i}',
                'url': f'https://bandcamp.com/fan{i}',
                'bio': f'Fan of {query} music' if query else f'Music lover',
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK']),
                'collection_count': random.randint(10, 500),
                'wishlist_count': random.randint(5, 100),
                'following_count': random.randint(20, 200),
                'follower_count': random.randint(5, 100),
                'genres': [query] if query else ['indie', 'experimental', 'electronic'],
                'signup_date': (datetime.utcnow() - timedelta(days=random.randint(365, 3650))).isoformat()
            })
        
        return fans
    
    async def _get_discover_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get discover page content"""
        content = []
        
        for i in range(min(max_results, 20)):
            content.append({
                'title': f'Featured: {query} {i}' if query else f'Featured Content {i}',
                'url': f'https://artist{i}.bandcamp.com/featured',
                'description': f'Featured content about {query}' if query else f'Featured description {i}',
                'genre': query if query else random.choice(['indie', 'experimental', 'electronic']),
                'location': random.choice(['Brooklyn, NY', 'Berlin, Germany', 'Tokyo, Japan', 'London, UK'])
            })
        
        return content
    
    async def _get_genres(self) -> List[str]:
        """Get available genres"""
        return [
            'indie', 'experimental', 'electronic', 'ambient', 'rock', 'folk',
            'jazz', 'classical', 'hip-hop', 'punk', 'metal', 'pop', 'world',
            'acoustic', 'instrumental', 'noise', 'drone', 'techno', 'house',
            'alternative'
        ]
    
    async def _get_genre_content(self, genre: str, max_results: int) -> List[Dict[str, Any]]:
        """Get content for specific genre"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'{genre.title()} Release {i}',
                'url': f'https://artist{i}.bandcamp.com/{genre}',
                'description': f'Independent {genre} music',
                'type': random.choice(['album', 'track', 'artist'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_track_data(self, track_data: Dict[str, Any]) -> Optional[BandcampTrack]:
        """Parse track data"""
        try:
            release_date = datetime.fromisoformat(track_data.get('release_date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            track = BandcampTrack(
                track_id=track_data.get('id', ''),
                title=track_data.get('title', ''),
                artist_name=track_data.get('artist_name', ''),
                artist_url=f"https://{track_data.get('artist_name', 'artist').lower().replace(' ', '')}.bandcamp.com",
                album_title=track_data.get('album_title', ''),
                album_url=f"https://{track_data.get('artist_name', 'artist').lower().replace(' ', '')}.bandcamp.com/album/{track_data.get('album_title', 'album').lower().replace(' ', '-')}",
                duration=track_data.get('duration', 0),
                track_number=track_data.get('track_number', 1),
                price=track_data.get('price'),
                currency=track_data.get('currency', 'USD'),
                streaming_url=None,
                download_url=None,
                lyrics=track_data.get('lyrics'),
                credits=track_data.get('credits', ''),
                about=track_data.get('about', ''),
                tags=track_data.get('tags', []),
                release_date=release_date,
                license_type=track_data.get('license_type', 'all-rights-reserved'),
                is_downloadable=track_data.get('is_downloadable', True),
                is_streamable=track_data.get('is_streamable', True),
                play_count=track_data.get('play_count', 0),
                favorite_count=track_data.get('favorite_count', 0),
                comment_count=track_data.get('comment_count', 0),
                purchase_count=track_data.get('purchase_count', 0),
                artwork_url='',
                file_formats=['mp3', 'flac'],
                min_price=track_data.get('min_price'),
                suggested_price=track_data.get('suggested_price'),
                location=track_data.get('location'),
                label=track_data.get('label')
            )
            
            return track
            
        except Exception as e:
            self.logger.error(f"Error parsing track data: {str(e)}")
            return None
    
    async def _parse_album_data(self, album_data: Dict[str, Any]) -> Optional[BandcampAlbum]:
        """Parse album data"""
        try:
            release_date = datetime.fromisoformat(album_data.get('release_date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            album = BandcampAlbum(
                album_id=album_data.get('id', ''),
                title=album_data.get('title', ''),
                artist_name=album_data.get('artist_name', ''),
                artist_url=f"https://{album_data.get('artist_name', 'artist').lower().replace(' ', '')}.bandcamp.com",
                url=album_data.get('url', ''),
                description=album_data.get('description', ''),
                release_date=release_date,
                tags=album_data.get('tags', []),
                track_count=album_data.get('track_count', 0),
                tracks=album_data.get('tracks', []),
                price=album_data.get('price'),
                currency=album_data.get('currency', 'USD'),
                min_price=album_data.get('min_price'),
                suggested_price=album_data.get('suggested_price'),
                is_preorder=album_data.get('is_preorder', False),
                release_type=album_data.get('release_type', 'album'),
                artwork_url='',
                credits=album_data.get('credits', ''),
                license_type=album_data.get('license_type', 'all-rights-reserved'),
                is_downloadable=album_data.get('is_downloadable', True),
                is_streamable=album_data.get('is_streamable', True),
                purchase_count=album_data.get('purchase_count', 0),
                favorite_count=album_data.get('favorite_count', 0),
                comment_count=album_data.get('comment_count', 0),
                wishlist_count=album_data.get('wishlist_count', 0),
                supported_by_count=album_data.get('supported_by_count', 0),
                location=album_data.get('location'),
                label=album_data.get('label'),
                catalog_number=album_data.get('catalog_number'),
                upc=album_data.get('upc')
            )
            
            return album
            
        except Exception as e:
            self.logger.error(f"Error parsing album data: {str(e)}")
            return None
    
    async def _parse_artist_data(self, artist_data: Dict[str, Any]) -> Optional[BandcampArtist]:
        """Parse artist data"""
        try:
            signup_date = None
            if artist_data.get('signup_date'):
                signup_date = datetime.fromisoformat(artist_data['signup_date'].replace('Z', '+00:00'))
            
            artist = BandcampArtist(
                artist_id=artist_data.get('id', ''),
                name=artist_data.get('name', ''),
                url=artist_data.get('url', ''),
                bio=artist_data.get('bio', ''),
                location=artist_data.get('location'),
                website=artist_data.get('website'),
                facebook_url=artist_data.get('facebook_url'),
                twitter_url=artist_data.get('twitter_url'),
                instagram_url=artist_data.get('instagram_url'),
                youtube_url=artist_data.get('youtube_url'),
                spotify_url=artist_data.get('spotify_url'),
                bandcamp_url=artist_data.get('url', ''),
                image_url='',
                banner_url=None,
                follower_count=artist_data.get('follower_count', 0),
                following_count=artist_data.get('following_count', 0),
                album_count=artist_data.get('album_count', 0),
                track_count=artist_data.get('track_count', 0),
                wishlist_count=artist_data.get('wishlist_count', 0),
                collection_count=artist_data.get('collection_count', 0),
                genres=artist_data.get('genres', []),
                labels=artist_data.get('labels', []),
                discography=artist_data.get('discography', []),
                featured_track=artist_data.get('featured_track'),
                is_label=artist_data.get('is_label', False),
                is_verified=artist_data.get('is_verified', False),
                signup_date=signup_date,
                last_active=None
            )
            
            return artist
            
        except Exception as e:
            self.logger.error(f"Error parsing artist data: {str(e)}")
            return None
    
    async def _parse_label_data(self, label_data: Dict[str, Any]) -> Optional[BandcampLabel]:
        """Parse label data"""
        try:
            established_date = None
            if label_data.get('established_date'):
                established_date = datetime.fromisoformat(label_data['established_date'].replace('Z', '+00:00'))
            
            label = BandcampLabel(
                label_id=label_data.get('id', ''),
                name=label_data.get('name', ''),
                url=label_data.get('url', ''),
                description=label_data.get('description', ''),
                location=label_data.get('location'),
                website=label_data.get('website'),
                contact_email=label_data.get('contact_email'),
                image_url='',
                banner_url=None,
                artist_count=label_data.get('artist_count', 0),
                release_count=label_data.get('release_count', 0),
                follower_count=label_data.get('follower_count', 0),
                artists=label_data.get('artists', []),
                releases=label_data.get('releases', []),
                genres=label_data.get('genres', []),
                featured_release=label_data.get('featured_release'),
                established_date=established_date,
                social_links=label_data.get('social_links', {})
            )
            
            return label
            
        except Exception as e:
            self.logger.error(f"Error parsing label data: {str(e)}")
            return None
    
    async def _parse_fan_data(self, fan_data: Dict[str, Any]) -> Optional[BandcampFan]:
        """Parse fan data"""
        try:
            signup_date = None
            if fan_data.get('signup_date'):
                signup_date = datetime.fromisoformat(fan_data['signup_date'].replace('Z', '+00:00'))
            
            fan = BandcampFan(
                fan_id=fan_data.get('id', ''),
                username=fan_data.get('username', ''),
                display_name=fan_data.get('display_name', ''),
                url=fan_data.get('url', ''),
                bio=fan_data.get('bio'),
                location=fan_data.get('location'),
                image_url='',
                following_count=fan_data.get('following_count', 0),
                follower_count=fan_data.get('follower_count', 0),
                collection_count=fan_data.get('collection_count', 0),
                wishlist_count=fan_data.get('wishlist_count', 0),
                collection=fan_data.get('collection', []),
                wishlist=fan_data.get('wishlist', []),
                following_artists=fan_data.get('following_artists', []),
                following_labels=fan_data.get('following_labels', []),
                following_fans=fan_data.get('following_fans', []),
                genres=fan_data.get('genres', []),
                signup_date=signup_date,
                last_active=None
            )
            
            return fan
            
        except Exception as e:
            self.logger.error(f"Error parsing fan data: {str(e)}")
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
        """Extract metadata from Bandcamp content"""
        try:
            # Parse Bandcamp URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'bandcamp',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Bandcamp URLs
            if 'bandcamp.com' in parsed_url.netloc:
                # Artist/label URL: artist.bandcamp.com
                if parsed_url.netloc != 'bandcamp.com':
                    subdomain = parsed_url.netloc.split('.')[0]
                    metadata.update({
                        'artist_name': subdomain,
                        'content_type': 'artist_page'
                    })
                    
                    # Album/track URL: artist.bandcamp.com/album/name or artist.bandcamp.com/track/name
                    path_parts = parsed_url.path.strip('/').split('/')
                    if len(path_parts) >= 2:
                        content_type = path_parts[0]  # album, track
                        content_name = path_parts[1]
                        metadata.update({
                            'content_type': content_type,
                            'content_name': content_name
                        })
                
                # General Bandcamp URL: bandcamp.com/...
                else:
                    path_parts = parsed_url.path.strip('/').split('/')
                    if path_parts:
                        metadata['page_type'] = path_parts[0]
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Bandcamp metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Bandcamp platform information"""
        return {
            'platform_name': 'Bandcamp',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Track content tracking',
                'Album monitoring',
                'Artist profile analysis',
                'Label tracking',
                'Fan activity monitoring',
                'Genre-based discovery',
                'Sales and pricing analysis',
                'Independent music discovery',
                'Artist support tracking',
                'Music collection analysis'
            ],
            'authentication': {
                'required': False,
                'type': 'None (Public scraping)',
                'scope': 'Public content access'
            },
            'content_characteristics': {
                'independent_focused': True,
                'high_quality_audio': True,
                'direct_artist_support': True,
                'pay_what_you_want': True
            },
            'limitations': [
                'No official API',
                'Rate limiting recommended',
                'Some content behind paywall',
                'Regional restrictions may apply'
            ]
        }
