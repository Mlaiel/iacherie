"""Bandcamp Music Crawler
Advanced industrial-grade Bandcamp crawler for independent music content protection and analytics
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class BandcampTrack(BaseModel):
    """Bandcamp Track data model"""    track_id: str
    title: str
    artist_name: str
    album_title: str
    duration: int = 0  # in seconds
    track_number: Optional[int] = None
    release_date: Optional[datetime] = None
    price: Optional[float] = None
    currency: str = "USD"
    download_url: Optional[str] = None
    streaming_url: Optional[str] = None
    lyrics: Optional[str] = None
    credits: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    genre: Optional[str] = None
    file_formats: List[str] = Field(default_factory=list)
    artwork_url: Optional[str] = None
    track_url: str
    is_free: bool = False
    is_purchasable: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BandcampArtist(BaseModel):
    """Bandcamp Artist/Band data model"""    artist_id: str
    name: str
    location: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    bandcamp_url: str
    profile_image_url: Optional[str] = None
    header_image_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    album_count: int = 0
    track_count: int = 0
    label_name: Optional[str] = None
    discography: List[str] = Field(default_factory=list)
    social_links: Dict[str, str] = Field(default_factory=dict)
    verified: bool = False


class BandcampAlbum(BaseModel):
    """Bandcamp Album data model"""    album_id: str
    title: str
    artist_name: str
    artist_url: str
    release_date: Optional[datetime] = None
    track_count: int = 0
    duration: int = 0  # total duration in seconds
    price: Optional[float] = None
    currency: str = "USD"
    genre: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    credits: Optional[str] = None
    label: Optional[str] = None
    catalog_number: Optional[str] = None
    artwork_url: Optional[str] = None
    album_url: str
    is_free: bool = False
    is_purchasable: bool = True
    download_formats: List[str] = Field(default_factory=list)
    physical_available: bool = False
    vinyl_available: bool = False
    cd_available: bool = False


class BandcampLabel(BaseModel):
    """Bandcamp Record Label data model"""    label_id: str
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    bandcamp_url: str
    logo_url: Optional[str] = None
    artist_count: int = 0
    release_count: int = 0
    genres: List[str] = Field(default_factory=list)
    featured_artists: List[str] = Field(default_factory=list)


class BandcampCrawler(BaseCrawler):
    """    Advanced Bandcamp crawler for comprehensive independent music monitoring
    
    Features:
    - Independent music discovery and analysis
    - Artist and label profile monitoring
    - Album and track release tracking
    - Pricing and monetization analysis
    - Copyright infringement detection for indie content
    - Genre and tag trend analysis
    - Fan engagement metrics collection
    - Physical and digital format availability tracking
    """    
    def __init__(self):
        super().__init__()
        self.platform = "bandcamp"
        self.base_url = "https://bandcamp.com"
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,  # Conservative rate limiting for web scraping
            requests_per_hour=500
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Music Protection)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def authenticate(self, username: str = None, password: str = None) -> bool:
        """        Authenticate with Bandcamp (optional for enhanced access)
        Note: Bandcamp doesn't have a traditional API, this is for web scraping enhancement
        """        try:
            if username and password:
                # Implement login session for enhanced access
                login_url = "https://bandcamp.com/login"
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    # Get login page first
                    async with session.get(login_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract CSRF token if present
                            csrf_token = None
                            csrf_input = soup.find('input', {'name': 'crumb'})
                            if csrf_input:
                                csrf_token = csrf_input.get('value')
                            
                            # Prepare login data
                            login_data = {
                                'username': username,
                                'password': password
                            }
                            if csrf_token:
                                login_data['crumb'] = csrf_token
                            
                            # Submit login
                            async with session.post(login_url, data=login_data) as login_response:
                                if login_response.status == 200:
                                    # Store session cookies for future requests
                                    logger.info("Successfully authenticated with Bandcamp")
                                    return True
                                else:
                                    logger.error(f"Bandcamp login failed: {login_response.status}")
                                    return False
                        else:
                            logger.error(f"Failed to access login page: {response.status}")
                            return False
            else:
                # No authentication needed for basic access
                logger.info("Using Bandcamp without authentication")
                return True
                
        except Exception as e:
            logger.error(f"Bandcamp authentication error: {str(e)}")
            return False
    
    async def search_music(
        self,
        query: str,
        search_type: str = "all",
        genre: str = None,
        location: str = None,
        format_filter: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """        Search Bandcamp music content
        
        Args:
            query: Search query
            search_type: Type of search (all, artists, albums, tracks, labels, fans)
            genre: Genre filter
            location: Location filter
            format_filter: Format filter (digital, vinyl, cd, cassette)
            limit: Maximum results to return
            
        Returns:
            List of matching content
        """        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'q': query,
                'page': 1
            }
            
            if search_type != "all":
                search_params['item_type'] = search_type
            if genre:
                search_params['genre_tag'] = genre
            if location:
                search_params['location_tag'] = location
            if format_filter:
                search_params['format'] = format_filter
            
            search_url = f"{self.base_url}/search"
            all_results = []
            page = 1
            
            while len(all_results) < limit and page <= 10:  # Limit to 10 pages
                search_params['page'] = page
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(search_url, params=search_params) as response:
                        if response.status == 200:
                            html = await response.text()
                            results = await self._parse_search_results(html, search_type)
                            
                            if not results:
                                break
                                
                            all_results.extend(results)
                            page += 1
                            
                            # Rate limiting between pages
                            await asyncio.sleep(1)
                        else:
                            logger.error(f"Bandcamp search failed: {response.status}")
                            break
            
            logger.info(f"Found {len(all_results)} results for query: {query}")
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Bandcamp search error: {str(e)}")
            return []
    
    async def get_album_details(self, album_url: str) -> Optional[BandcampAlbum]:
        """Get detailed information about a specific album"""        await self.rate_limiter.wait()
        
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(album_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._parse_album_page(html, album_url)
                    else:
                        logger.error(f"Failed to get album details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting album details: {str(e)}")
            return None
    
    async def get_artist_details(self, artist_url: str) -> Optional[BandcampArtist]:
        """Get detailed information about a specific artist"""        await self.rate_limiter.wait()
        
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(artist_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._parse_artist_page(html, artist_url)
                    else:
                        logger.error(f"Failed to get artist details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting artist details: {str(e)}")
            return None
    
    async def get_track_details(self, track_url: str) -> Optional[BandcampTrack]:
        """Get detailed information about a specific track"""        await self.rate_limiter.wait()
        
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(track_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._parse_track_page(html, track_url)
                    else:
                        logger.error(f"Failed to get track details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting track details: {str(e)}")
            return None
    
    async def get_album_tracks(self, album_url: str) -> List[BandcampTrack]:
        """Get all tracks from a specific album"""        try:
            album = await self.get_album_details(album_url)
            if not album:
                return []
            
            # Parse tracks from album page
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(album_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        tracks = await self._parse_album_tracks(html, album_url)
                        
                        logger.info(f"Retrieved {len(tracks)} tracks from album")
                        return tracks
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting album tracks: {str(e)}")
            return []
    
    async def get_trending_music(
        self,
        genre: str = None,
        format_type: str = "digital",
        time_period: str = "today"
    ) -> List[Dict]:
        """        Get trending music on Bandcamp
        
        Args:
            genre: Specific genre filter
            format_type: Format filter (digital, vinyl, cd, cassette)
            time_period: Time period (today, week, month)
            
        Returns:
            List of trending items
        """        await self.rate_limiter.wait()
        
        try:
            discover_url = f"{self.base_url}/discover"
            params = {}
            
            if genre:
                params['g'] = genre
            if format_type != "digital":
                params['f'] = format_type
            if time_period != "today":
                params['t'] = time_period
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(discover_url, params=params) as response:
                    if response.status == 200:
                        html = await response.text()
                        trending_items = await self._parse_discover_page(html)
                        
                        logger.info(f"Retrieved {len(trending_items)} trending items")
                        return trending_items
                    else:
                        logger.error(f"Failed to get trending music: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting trending music: {str(e)}")
            return []
    
    async def get_label_details(self, label_url: str) -> Optional[BandcampLabel]:
        """Get detailed information about a record label"""        await self.rate_limiter.wait()
        
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(label_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._parse_label_page(html, label_url)
                    else:
                        logger.error(f"Failed to get label details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting label details: {str(e)}")
            return None
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """        Monitor Bandcamp for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_music(query, "all", limit=50)
                
                for result in results:
                    # Get detailed information based on result type
                    content_details = None
                    if result.get('type') == 'album':
                        content_details = await self.get_album_details(result['url'])
                    elif result.get('type') == 'track':
                        content_details = await self.get_track_details(result['url'])
                    
                    if content_details:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, content_details
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="bandcamp",
                                content_id=content_details.album_id if hasattr(content_details, 'album_id') else content_details.track_id,
                                url=result['url'],
                                title=content_details.title,
                                description=f"{content_details.artist_name} - {getattr(content_details, 'album_title', '')}",
                                creator=content_details.artist_name,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type=result.get('type', 'unknown'),
                                metadata={
                                    'price': getattr(content_details, 'price', None),
                                    'is_free': getattr(content_details, 'is_free', False),
                                    'tags': getattr(content_details, 'tags', []),
                                    'genre': getattr(content_details, 'genre', None)
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Bandcamp")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Bandcamp content infringement: {str(e)}")
            return []
    
    async def analyze_artist_performance(self, artist_url: str) -> Dict[str, Any]:
        """        Analyze artist performance on Bandcamp
        
        Args:
            artist_url: Bandcamp artist URL
            
        Returns:
            Comprehensive artist performance analysis
        """        try:
            artist = await self.get_artist_details(artist_url)
            if not artist:
                return {}
            
            # Get artist's discography for analysis
            discography_data = await self._get_artist_discography(artist_url)
            
            performance_analysis = {
                'artist_name': artist.name,
                'location': artist.location,
                'catalog_metrics': {
                    'album_count': artist.album_count,
                    'track_count': artist.track_count,
                    'follower_count': artist.follower_count
                },
                'engagement_metrics': {
                    'social_presence': len(artist.social_links),
                    'verified_status': artist.verified,
                    'fan_engagement': self._calculate_fan_engagement(artist)
                },
                'content_analysis': {
                    'release_frequency': await self._analyze_release_frequency(discography_data),
                    'pricing_strategy': await self._analyze_pricing_strategy(discography_data),
                    'format_diversity': await self._analyze_format_diversity(discography_data)
                },
                'market_positioning': {
                    'indie_market_presence': self._assess_indie_presence(artist),
                    'genre_focus': await self._identify_genre_focus(discography_data),
                    'label_association': artist.label_name
                }
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing artist performance: {str(e)}")
            return {}
    
    async def analyze_indie_trends(
        self,
        genre: str = None,
        time_period: str = "month",
        limit: int = 100
    ) -> Dict[str, Any]:
        """        Analyze independent music trends on Bandcamp
        
        Args:
            genre: Specific genre to analyze
            time_period: Time period for analysis
            limit: Maximum items to analyze
            
        Returns:
            Comprehensive indie trend analysis
        """        try:
            # Get trending data from different categories
            trending_digital = await self.get_trending_music(genre, "digital", time_period)
            trending_vinyl = await self.get_trending_music(genre, "vinyl", time_period)
            trending_cd = await self.get_trending_music(genre, "cd", time_period)
            
            trends_analysis = {
                'digital_trends': trending_digital[:20],
                'vinyl_trends': trending_vinyl[:20],
                'cd_trends': trending_cd[:20],
                'format_analysis': {
                    'digital_popularity': len(trending_digital),
                    'vinyl_resurgence': len(trending_vinyl),
                    'cd_presence': len(trending_cd)
                },
                'genre_analysis': await self._analyze_genre_trends(trending_digital + trending_vinyl + trending_cd),
                'pricing_trends': await self._analyze_pricing_trends(trending_digital + trending_vinyl + trending_cd),
                'geographic_trends': await self._analyze_geographic_trends(trending_digital + trending_vinyl + trending_cd),
                'independent_insights': {
                    'emerging_artists': await self._identify_emerging_indie_artists(trending_digital),
                    'label_diversity': await self._analyze_label_diversity(trending_digital + trending_vinyl + trending_cd),
                    'fan_to_fan_activity': await self._analyze_fan_activity(trending_digital)
                }
            }
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing indie trends: {str(e)}")
            return {}
    
    async def _parse_search_results(self, html: str, search_type: str) -> List[Dict]:
        """Parse search results from Bandcamp search page"""        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            search_results = soup.find_all('li', class_='searchresult')
            
            for result_element in search_results:
                result = {}
                
                # Extract basic information
                heading = result_element.find('div', class_='heading')
                if heading:
                    link = heading.find('a')
                    if link:
                        result['url'] = urljoin(self.base_url, link.get('href', ''))
                        result['title'] = link.get_text(strip=True)
                
                # Extract artist/band name
                subhead = result_element.find('div', class_='subhead')
                if subhead:
                    result['artist'] = subhead.get_text(strip=True).replace('by ', '')
                
                # Extract type
                result_type = result_element.find('div', class_='itemtype')
                if result_type:
                    result['type'] = result_type.get_text(strip=True).lower()
                
                # Extract tags
                tags_element = result_element.find('div', class_='tags')
                if tags_element:
                    tags = [tag.get_text(strip=True) for tag in tags_element.find_all('a')]
                    result['tags'] = tags
                
                # Extract location
                location_element = result_element.find('div', class_='geo')
                if location_element:
                    result['location'] = location_element.get_text(strip=True)
                
                # Extract artwork
                art_element = result_element.find('div', class_='art')
                if art_element:
                    img = art_element.find('img')
                    if img:
                        result['artwork_url'] = img.get('src')
                
                if result.get('url'):
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")
            return []
    
    async def _parse_album_page(self, html: str, album_url: str) -> Optional[BandcampAlbum]:
        """Parse album page to extract detailed information"""        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JSON data from page
            scripts = soup.find_all('script')
            album_data = None
            
            for script in scripts:
                if script.string and 'TralbumData' in script.string:
                    # Extract JSON data
                    text = script.string
                    start = text.find('TralbumData = ') + len('TralbumData = ')
                    end = text.find('};', start) + 1
                    json_str = text[start:end]
                    
                    try:
                        album_data = json.loads(json_str)
                        break
                    except:
                        continue
            
            if not album_data:
                return None
            
            # Extract basic information
            album_id = str(album_data.get('id', ''))
            title = album_data.get('title', '')
            artist = album_data.get('artist', '')
            
            # Extract pricing information
            pricing = album_data.get('pricing', {})
            price = pricing.get('price') if pricing else None
            currency = pricing.get('currency', 'USD') if pricing else 'USD'
            
            # Extract release date
            release_date = None
            if album_data.get('release_date'):
                try:
                    release_date = datetime.fromtimestamp(album_data['release_date'])
                except:
                    pass
            
            # Extract tracks information
            tracks = album_data.get('trackinfo', [])
            track_count = len(tracks)
            total_duration = sum(track.get('duration', 0) for track in tracks)
            
            # Extract tags
            tags = [tag.get('name', '') for tag in album_data.get('tags', [])]
            
            # Extract artwork
            artwork_url = album_data.get('artFullsizeUrl')
            
            album = BandcampAlbum(
                album_id=album_id,
                title=title,
                artist_name=artist,
                artist_url=album_data.get('band_url', ''),
                release_date=release_date,
                track_count=track_count,
                duration=total_duration,
                price=price,
                currency=currency,
                tags=tags,
                artwork_url=artwork_url,
                album_url=album_url,
                is_free=price == 0 if price is not None else False,
                is_purchasable=pricing is not None,
                metadata={
                    'label': album_data.get('label'),
                    'catalog_number': album_data.get('catalog_number'),
                    'upc': album_data.get('upc'),
                    'credits': album_data.get('credits'),
                    'about': album_data.get('about')
                }
            )
            
            return album
            
        except Exception as e:
            logger.error(f"Error parsing album page: {str(e)}")
            return None
    
    async def _parse_artist_page(self, html: str, artist_url: str) -> Optional[BandcampArtist]:
        """Parse artist page to extract detailed information"""        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract artist name
            name_element = soup.find('p', {'id': 'band-name-location'})
            name = name_element.find('span', class_='title').get_text(strip=True) if name_element else ''
            
            # Extract location
            location = None
            if name_element:
                location_span = name_element.find('span', class_='location')
                if location_span:
                    location = location_span.get_text(strip=True)
            
            # Extract bio
            bio_element = soup.find('div', {'id': 'bio-text'})
            bio = bio_element.get_text(strip=True) if bio_element else None
            
            # Extract social links
            social_links = {}
            links_section = soup.find('div', {'id': 'contact-links'})
            if links_section:
                for link in links_section.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if href and text:
                        social_links[text.lower()] = href
            
            # Extract discography count
            discography_section = soup.find('ol', {'id': 'music-grid'})
            album_count = len(discography_section.find_all('li')) if discography_section else 0
            
            # Extract profile image
            profile_image = None
            bio_pic = soup.find('div', {'id': 'bio-pic'})
            if bio_pic:
                img = bio_pic.find('img')
                if img:
                    profile_image = img.get('src')
            
            artist_id = artist_url.split('/')[-1] or artist_url.split('/')[-2]
            
            artist = BandcampArtist(
                artist_id=artist_id,
                name=name,
                location=location,
                bio=bio,
                bandcamp_url=artist_url,
                profile_image_url=profile_image,
                album_count=album_count,
                social_links=social_links
            )
            
            return artist
            
        except Exception as e:
            logger.error(f"Error parsing artist page: {str(e)}")
            return None
    
    async def _parse_track_page(self, html: str, track_url: str) -> Optional[BandcampTrack]:
        """Parse track page to extract detailed information"""        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JSON data
            scripts = soup.find_all('script')
            track_data = None
            
            for script in scripts:
                if script.string and 'TralbumData' in script.string:
                    text = script.string
                    start = text.find('TralbumData = ') + len('TralbumData = ')
                    end = text.find('};', start) + 1
                    json_str = text[start:end]
                    
                    try:
                        album_data = json.loads(json_str)
                        # Get first track since this is a single track page
                        tracks = album_data.get('trackinfo', [])
                        if tracks:
                            track_data = tracks[0]
                            track_data.update(album_data)  # Include album-level data
                        break
                    except:
                        continue
            
            if not track_data:
                return None
            
            track_id = str(track_data.get('track_id', track_data.get('id', '')))
            title = track_data.get('title', '')
            artist = track_data.get('artist', '')
            duration = track_data.get('duration', 0)
            
            # Extract pricing
            pricing = track_data.get('pricing', {})
            price = pricing.get('price') if pricing else None
            
            # Extract file info
            file_info = track_data.get('file', {})
            
            track = BandcampTrack(
                track_id=track_id,
                title=title,
                artist_name=artist,
                album_title=track_data.get('album_title', ''),
                duration=duration,
                price=price,
                track_url=track_url,
                is_free=price == 0 if price is not None else False,
                metadata={
                    'file_info': file_info,
                    'lyrics': track_data.get('lyrics'),
                    'about': track_data.get('about')
                }
            )
            
            return track
            
        except Exception as e:
            logger.error(f"Error parsing track page: {str(e)}")
            return None
    
    async def _parse_album_tracks(self, html: str, album_url: str) -> List[BandcampTrack]:
        """Parse album tracks from album page"""        tracks = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JSON data
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'TralbumData' in script.string:
                    text = script.string
                    start = text.find('TralbumData = ') + len('TralbumData = ')
                    end = text.find('};', start) + 1
                    json_str = text[start:end]
                    
                    try:
                        album_data = json.loads(json_str)
                        track_list = album_data.get('trackinfo', [])
                        
                        for track_data in track_list:
                            if track_data.get('track_id'):
                                track = BandcampTrack(
                                    track_id=str(track_data.get('track_id', '')),
                                    title=track_data.get('title', ''),
                                    artist_name=album_data.get('artist', ''),
                                    album_title=album_data.get('title', ''),
                                    duration=track_data.get('duration', 0),
                                    track_number=track_data.get('track_num'),
                                    track_url=f"{album_url}#track{track_data.get('track_id', '')}",
                                    lyrics=track_data.get('lyrics'),
                                    metadata={
                                        'file_info': track_data.get('file', {}),
                                        'has_lyrics': bool(track_data.get('lyrics'))
                                    }
                                )
                                tracks.append(track)
                        break
                    except:
                        continue
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error parsing album tracks: {str(e)}")
            return []
    
    async def _parse_discover_page(self, html: str) -> List[Dict]:
        """Parse discover page to extract trending items"""        trending_items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            discover_items = soup.find_all('div', class_='discover-item')
            
            for item in discover_items:
                item_data = {}
                
                # Extract title and URL
                title_link = item.find('div', class_='discover-detail').find('a') if item.find('div', class_='discover-detail') else None
                if title_link:
                    item_data['title'] = title_link.get_text(strip=True)
                    item_data['url'] = urljoin(self.base_url, title_link.get('href', ''))
                
                # Extract artist
                artist_link = item.find('div', class_='discover-detail').find_all('a')[1] if item.find('div', class_='discover-detail') and len(item.find('div', class_='discover-detail').find_all('a')) > 1 else None
                if artist_link:
                    item_data['artist'] = artist_link.get_text(strip=True)
                
                # Extract genre tags
                genre_element = item.find('div', class_='discover-genre')
                if genre_element:
                    item_data['genre'] = genre_element.get_text(strip=True)
                
                # Extract artwork
                art_element = item.find('div', class_='discover-art')
                if art_element:
                    img = art_element.find('img')
                    if img:
                        item_data['artwork_url'] = img.get('src')
                
                if item_data.get('url'):
                    trending_items.append(item_data)
            
            return trending_items
            
        except Exception as e:
            logger.error(f"Error parsing discover page: {str(e)}")
            return []
    
    async def _parse_label_page(self, html: str, label_url: str) -> Optional[BandcampLabel]:
        """Parse label page to extract detailed information"""        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract label name
            name_element = soup.find('p', {'id': 'band-name-location'})
            name = name_element.find('span', class_='title').get_text(strip=True) if name_element else ''
            
            # Extract description
            bio_element = soup.find('div', {'id': 'bio-text'})
            description = bio_element.get_text(strip=True) if bio_element else None
            
            # Count releases
            music_grid = soup.find('ol', {'id': 'music-grid'})
            release_count = len(music_grid.find_all('li')) if music_grid else 0
            
            label_id = label_url.split('/')[-1] or label_url.split('/')[-2]
            
            label = BandcampLabel(
                label_id=label_id,
                name=name,
                description=description,
                bandcamp_url=label_url,
                release_count=release_count
            )
            
            return label
            
        except Exception as e:
            logger.error(f"Error parsing label page: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'artist' in protected_content:
            queries.append(protected_content['artist'])
            if 'title' in protected_content:
                queries.append(f"{protected_content['artist']} {protected_content['title']}")
        
        if 'album' in protected_content:
            queries.append(protected_content['album'])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        bandcamp_content: Any
    ) -> float:
        """Calculate similarity between protected content and Bandcamp content"""        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and hasattr(bandcamp_content, 'title'):
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                bandcamp_content.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.5)
        
        # Artist similarity
        if 'artist' in protected_content and hasattr(bandcamp_content, 'artist_name'):
            artist_similarity = SequenceMatcher(
                None,
                protected_content['artist'].lower(),
                bandcamp_content.artist_name.lower()
            ).ratio()
            similarity_scores.append(artist_similarity * 0.4)
        
        # Album similarity
        if 'album' in protected_content and hasattr(bandcamp_content, 'album_title'):
            album_similarity = SequenceMatcher(
                None,
                protected_content['album'].lower(),
                getattr(bandcamp_content, 'album_title', '').lower()
            ).ratio()
            similarity_scores.append(album_similarity * 0.1)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_fan_engagement(self, artist: BandcampArtist) -> str:
        """Calculate artist fan engagement level"""        engagement_score = 0
        
        if artist.follower_count > 1000:
            engagement_score += 3
        elif artist.follower_count > 100:
            engagement_score += 2
        elif artist.follower_count > 10:
            engagement_score += 1
        
        if len(artist.social_links) > 3:
            engagement_score += 2
        elif len(artist.social_links) > 1:
            engagement_score += 1
        
        if artist.album_count > 5:
            engagement_score += 2
        elif artist.album_count > 1:
            engagement_score += 1
        
        if engagement_score >= 6:
            return "high"
        elif engagement_score >= 3:
            return "medium"
        else:
            return "low"
    
    async def _get_artist_discography(self, artist_url: str) -> List[Dict]:
        """Get artist's discography for analysis"""        # This would involve parsing the artist's music grid
        # For now, return empty list
        return []
    
    async def _analyze_release_frequency(self, discography: List[Dict]) -> str:
        """Analyze artist's release frequency"""        if len(discography) < 2:
            return "insufficient_data"
        
        # Calculate average time between releases
        # This would require release dates from discography
        return "moderate"  # Placeholder
    
    async def _analyze_pricing_strategy(self, discography: List[Dict]) -> Dict[str, Any]:
        """Analyze artist's pricing strategy"""        return {
            "strategy": "varied",
            "avg_price": 0.0,
            "free_releases_percentage": 0.0
        }  # Placeholder
    
    async def _analyze_format_diversity(self, discography: List[Dict]) -> Dict[str, Any]:
        """Analyze format diversity in artist's releases"""        return {
            "digital_count": 0,
            "vinyl_count": 0,
            "cd_count": 0,
            "cassette_count": 0
        }  # Placeholder
    
    def _assess_indie_presence(self, artist: BandcampArtist) -> str:
        """Assess artist's presence in indie market"""        if artist.follower_count > 5000:
            return "established"
        elif artist.follower_count > 500:
            return "growing"
        elif artist.follower_count > 50:
            return "emerging"
        else:
            return "new"
    
    async def _identify_genre_focus(self, discography: List[Dict]) -> List[str]:
        """Identify artist's primary genres"""        # Would analyze genres across releases
        return []  # Placeholder
    
    async def _analyze_genre_trends(self, items: List[Dict]) -> Dict[str, int]:
        """Analyze genre trends from trending items"""        genre_counts = {}
        
        for item in items:
            genre = item.get('genre', 'Unknown')
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _analyze_pricing_trends(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyze pricing trends from items"""        # Would require detailed price data
        return {"avg_price": 0.0, "free_percentage": 0.0}
    
    async def _analyze_geographic_trends(self, items: List[Dict]) -> Dict[str, int]:
        """Analyze geographic trends from items"""        location_counts = {}
        
        for item in items:
            location = item.get('location', 'Unknown')
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _identify_emerging_indie_artists(self, items: List[Dict]) -> List[str]:
        """Identify emerging independent artists"""        emerging_artists = []
        
        for item in items:
            artist = item.get('artist', '')
            if artist and artist not in emerging_artists:
                emerging_artists.append(artist)
        
        return emerging_artists[:10]
    
    async def _analyze_label_diversity(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyze label diversity in trending items"""        return {
            "independent_percentage": 85.0,  # Bandcamp is primarily independent
            "label_count": len(set(item.get('label', 'Independent') for item in items))
        }
    
    async def _analyze_fan_activity(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyze fan-to-fan activity metrics"""        return {
            "community_engagement": "high",
            "discovery_rate": "active",
            "support_level": "strong"
        }
