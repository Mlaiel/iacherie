"""Spotify Crawler Implementation
=============================

Professional Spotify content crawler for copyright protection and content monitoring.
Implements Spotify Web API integration for music content discovery and analysis.

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
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


class SpotifyCrawler(PlatformCrawler):
    """
    Professional Spotify crawler for music content monitoring and copyright protection.
    
    Features:
    - Spotify Web API integration
    - Track and album search
    - Artist monitoring
    - Playlist analysis
    - Audio feature extraction
    - Real-time new releases tracking
    - Music recommendation analysis
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher,
                 client_id: str, client_secret: str):
        """
        Initialize Spotify crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
        """
        super().__init__(config, vector_matcher)
        
        # API credentials
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Spotify API client
        self.spotify_client = None
        self.access_token = None
        self.token_expires_at = None
        
        # Rate limiting parameters
        self.rate_limit_window = 60  # 1 minute
        self.requests_per_minute = 100  # Conservative limit
        self.current_requests = 0
        self.window_start = datetime.utcnow()
        
        # Search parameters
        self.max_tracks_per_search = 50
        self.supported_types = ['track', 'album', 'artist', 'playlist']
        self.markets = ['US', 'GB', 'DE', 'FR', 'ES', 'IT', 'CA', 'AU']
        
        # Initialize API client
        asyncio.create_task(self._initialize_api_client())
    
    async def _initialize_api_client(self):
        """Initialize Spotify Web API client"""
        try:
            # Set up client credentials flow
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            self.spotify_client = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager
            )
            
            # Test API connection
            await self._test_api_connection()
            
            self.logger.info("Spotify Web API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify API client: {str(e)}")
            raise
    
    async def _test_api_connection(self):
        """Test API connection"""
        try:
            # Test with simple API call
            featured_playlists = self.spotify_client.featured_playlists(limit=1)
            if featured_playlists:
                self.logger.info("Spotify API connection test successful")
                
        except Exception as e:
            self.logger.warning(f"Spotify API connection test failed: {str(e)}")
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for content on Spotify using Web API.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found music items
        """
        try:
            await self._check_rate_limit()
            
            all_results = []
            
            for term in search_terms[:5]:  # Limit for rate limiting
                try:
                    # Search across all content types
                    search_results = self.spotify_client.search(
                        q=term,
                        type='track,album,artist',
                        limit=min(max_results // len(search_terms), 50),
                        market='US'
                    )
                    
                    # Process tracks
                    if search_results.get('tracks', {}).get('items'):
                        track_results = await self._process_track_results(search_results['tracks']['items'])
                        all_results.extend(track_results)
                    
                    # Process albums
                    if search_results.get('albums', {}).get('items'):
                        album_results = await self._process_album_results(search_results['albums']['items'])
                        all_results.extend(album_results)
                    
                    # Process artists
                    if search_results.get('artists', {}).get('items'):
                        artist_results = await self._process_artist_results(search_results['artists']['items'])
                        all_results.extend(artist_results)
                    
                    # Apply rate limiting
                    await self._apply_rate_limit()
                    
                except Exception as e:
                    self.logger.error(f"Error searching Spotify for term '{term}': {str(e)}")
                    continue
            
            # Remove duplicates and sort by popularity
            unique_results = await self._deduplicate_results(all_results)
            
            self.logger.info(f"Found {len(unique_results)} unique Spotify items")
            return unique_results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error in Spotify search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """
        Extract metadata from Spotify content URL.
        
        Args:
            content_url: URL of the Spotify content
            
        Returns:
            Content metadata dictionary
        """
        try:
            # Extract Spotify ID and type from URL
            spotify_id, content_type = self._extract_spotify_id_from_url(content_url)
            if not spotify_id or not content_type:
                return {}
            
            # Get content details based on type
            if content_type == 'track':
                metadata = await self._get_track_metadata(spotify_id)
            elif content_type == 'album':
                metadata = await self._get_album_metadata(spotify_id)
            elif content_type == 'artist':
                metadata = await self._get_artist_metadata(spotify_id)
            elif content_type == 'playlist':
                metadata = await self._get_playlist_metadata(spotify_id)
            else:
                return {}
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download content sample for fingerprinting.
        Note: Spotify doesn't allow downloading full tracks, only 30-second previews.
        
        Args:
            content_url: URL of the content
            
        Returns:
            Preview audio data bytes or None if failed
        """
        try:
            # Extract track ID from URL
            spotify_id, content_type = self._extract_spotify_id_from_url(content_url)
            if not spotify_id or content_type != 'track':
                return None
            
            # Get track details including preview URL
            track = self.spotify_client.track(spotify_id)
            preview_url = track.get('preview_url')
            
            if preview_url:
                async with self.session.get(preview_url) as response:
                    if response.status == 200:
                        return await response.read()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading content sample: {str(e)}")
            return None
    
    async def search_by_artist(self, artist_name: str, 
                             max_tracks: int = 50) -> List[Dict[str, Any]]:
        """
        Search tracks by specific artist.
        
        Args:
            artist_name: Name of the artist
            max_tracks: Maximum number of tracks to return
            
        Returns:
            List of artist's tracks
        """
        try:
            # Search for artist first
            artist_results = self.spotify_client.search(
                q=f'artist:{artist_name}',
                type='artist',
                limit=1
            )
            
            if not artist_results.get('artists', {}).get('items'):
                return []
            
            artist = artist_results['artists']['items'][0]
            artist_id = artist['id']
            
            # Get artist's albums
            albums = self.spotify_client.artist_albums(
                artist_id,
                album_type='album,single',
                limit=20
            )
            
            all_tracks = []
            
            # Get tracks from each album
            for album in albums['items']:
                try:
                    album_tracks = self.spotify_client.album_tracks(album['id'])
                    
                    for track in album_tracks['items']:
                        track_data = await self._process_single_track(track, album)
                        all_tracks.append(track_data)
                        
                        if len(all_tracks) >= max_tracks:
                            break
                    
                    if len(all_tracks) >= max_tracks:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Error processing album {album['id']}: {str(e)}")
                    continue
            
            return all_tracks[:max_tracks]
            
        except Exception as e:
            self.logger.error(f"Error searching artist {artist_name}: {str(e)}")
            return []
    
    async def get_track_audio_features(self, track_id: str) -> Dict[str, Any]:
        """
        Get audio features for a specific track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Audio features dictionary
        """
        try:
            features = self.spotify_client.audio_features(track_id)
            
            if features and features[0]:
                return features[0]
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting audio features for {track_id}: {str(e)}")
            return {}
    
    async def analyze_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """
        Analyze a Spotify playlist for content monitoring.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist analysis data
        """
        try:
            # Get playlist info
            playlist = self.spotify_client.playlist(playlist_id)
            
            # Get all tracks
            tracks = []
            results = self.spotify_client.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            
            # Handle pagination
            while results['next']:
                results = self.spotify_client.next(results)
                tracks.extend(results['items'])
            
            # Analyze tracks
            track_analyses = []
            for item in tracks:
                if item['track']:
                    track_data = await self._process_single_track(item['track'])
                    
                    # Get audio features
                    audio_features = await self.get_track_audio_features(item['track']['id'])
                    track_data['audio_features'] = audio_features
                    
                    track_analyses.append(track_data)
            
            # Calculate playlist statistics
            analysis = {
                'playlist_id': playlist_id,
                'name': playlist.get('name'),
                'description': playlist.get('description'),
                'owner': playlist.get('owner', {}).get('display_name'),
                'total_tracks': len(track_analyses),
                'followers': playlist.get('followers', {}).get('total', 0),
                'tracks': track_analyses,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Calculate average audio features
            if track_analyses:
                avg_features = await self._calculate_average_audio_features(track_analyses)
                analysis['average_audio_features'] = avg_features
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing playlist {playlist_id}: {str(e)}")
            return {}
    
    async def monitor_new_releases(self, country: str = 'US', 
                                 callback_url: str = None) -> str:
        """
        Monitor new releases on Spotify.
        
        Args:
            country: Country code for new releases
            callback_url: Optional callback URL for notifications
            
        Returns:
            Monitoring session ID
        """
        try:
            monitoring_id = f"spotify_releases_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Get current new releases for comparison
            current_releases = self.spotify_client.new_releases(
                country=country,
                limit=50
            )
            
            current_album_ids = {album['id'] for album in current_releases['albums']['items']}
            
            # Create monitoring task
            async def monitoring_task():
                known_albums = current_album_ids.copy()
                
                while True:
                    try:
                        # Check for new releases
                        new_releases = self.spotify_client.new_releases(
                            country=country,
                            limit=50
                        )
                        
                        # Find truly new releases
                        new_album_ids = {album['id'] for album in new_releases['albums']['items']}
                        truly_new = new_album_ids - known_albums
                        
                        if truly_new:
                            # Process new releases
                            for album in new_releases['albums']['items']:
                                if album['id'] in truly_new:
                                    if callback_url:
                                        await self._send_new_release_notification(
                                            album, callback_url, monitoring_id
                                        )
                            
                            # Update known albums
                            known_albums.update(truly_new)
                        
                        # Wait before next check (check every hour)
                        await asyncio.sleep(3600)
                        
                    except Exception as e:
                        self.logger.error(f"Error in new releases monitoring: {str(e)}")
                        await asyncio.sleep(1800)  # Wait 30 minutes on error
            
            # Start monitoring task
            asyncio.create_task(monitoring_task())
            
            self.logger.info(f"Started Spotify new releases monitoring: {monitoring_id}")
            return monitoring_id
            
        except Exception as e:
            self.logger.error(f"Error starting new releases monitoring: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _process_track_results(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process track search results"""
        processed_tracks = []
        
        for track in tracks:
            try:
                processed_track = await self._process_single_track(track)
                processed_tracks.append(processed_track)
                
            except Exception as e:
                self.logger.warning(f"Error processing track {track.get('id')}: {str(e)}")
                continue
        
        return processed_tracks
    
    async def _process_album_results(self, albums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process album search results"""
        processed_albums = []
        
        for album in albums:
            try:
                processed_album = {
                    'url': album.get('external_urls', {}).get('spotify', ''),
                    'title': album.get('name', ''),
                    'description': f"Album by {', '.join(artist['name'] for artist in album.get('artists', []))}",
                    'author': ', '.join(artist['name'] for artist in album.get('artists', [])),
                    'upload_date': self._parse_release_date(album.get('release_date')),
                    'album_id': album.get('id'),
                    'album_type': album.get('album_type'),
                    'total_tracks': album.get('total_tracks', 0),
                    'popularity': album.get('popularity', 0),
                    'genres': album.get('genres', []),
                    'label': album.get('label', ''),
                    'image_url': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
                    'content_type': 'album'
                }
                
                processed_albums.append(processed_album)
                
            except Exception as e:
                self.logger.warning(f"Error processing album {album.get('id')}: {str(e)}")
                continue
        
        return processed_albums
    
    async def _process_artist_results(self, artists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process artist search results"""
        processed_artists = []
        
        for artist in artists:
            try:
                processed_artist = {
                    'url': artist.get('external_urls', {}).get('spotify', ''),
                    'title': artist.get('name', ''),
                    'description': f"Artist - {', '.join(artist.get('genres', []))}",
                    'author': artist.get('name', ''),
                    'artist_id': artist.get('id'),
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0),
                    'genres': artist.get('genres', []),
                    'image_url': artist.get('images', [{}])[0].get('url', '') if artist.get('images') else '',
                    'content_type': 'artist'
                }
                
                processed_artists.append(processed_artist)
                
            except Exception as e:
                self.logger.warning(f"Error processing artist {artist.get('id')}: {str(e)}")
                continue
        
        return processed_artists
    
    async def _process_single_track(self, track: Dict[str, Any], 
                                  album: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process single track data"""
        try:
            # Use provided album data or track's album data
            album_data = album or track.get('album', {})
            
            processed_track = {
                'url': track.get('external_urls', {}).get('spotify', ''),
                'title': track.get('name', ''),
                'description': f"Track by {', '.join(artist['name'] for artist in track.get('artists', []))}",
                'author': ', '.join(artist['name'] for artist in track.get('artists', [])),
                'upload_date': self._parse_release_date(album_data.get('release_date')),
                'track_id': track.get('id'),
                'album_name': album_data.get('name', ''),
                'album_id': album_data.get('id'),
                'duration_ms': track.get('duration_ms', 0),
                'popularity': track.get('popularity', 0),
                'explicit': track.get('explicit', False),
                'track_number': track.get('track_number', 1),
                'disc_number': track.get('disc_number', 1),
                'isrc': track.get('external_ids', {}).get('isrc'),
                'preview_url': track.get('preview_url'),
                'image_url': album_data.get('images', [{}])[0].get('url', '') if album_data.get('images') else '',
                'content_type': 'track'
            }
            
            return processed_track
            
        except Exception as e:
            self.logger.error(f"Error processing single track: {str(e)}")
            return {}
    
    async def _get_track_metadata(self, track_id: str) -> Dict[str, Any]:
        """Get detailed track metadata"""
        try:
            track = self.spotify_client.track(track_id)
            audio_features = await self.get_track_audio_features(track_id)
            
            metadata = await self._process_single_track(track)
            metadata['audio_features'] = audio_features
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error getting track metadata: {str(e)}")
            return {}
    
    async def _get_album_metadata(self, album_id: str) -> Dict[str, Any]:
        """Get detailed album metadata"""
        try:
            album = self.spotify_client.album(album_id)
            
            # Process album info
            metadata = {
                'album_id': album.get('id'),
                'name': album.get('name'),
                'artists': [artist['name'] for artist in album.get('artists', [])],
                'release_date': album.get('release_date'),
                'total_tracks': album.get('total_tracks', 0),
                'genres': album.get('genres', []),
                'label': album.get('label', ''),
                'popularity': album.get('popularity', 0),
                'image_url': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
                'tracks': []
            }
            
            # Add track information
            for track in album.get('tracks', {}).get('items', []):
                track_data = await self._process_single_track(track, album)
                metadata['tracks'].append(track_data)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error getting album metadata: {str(e)}")
            return {}
    
    async def _get_artist_metadata(self, artist_id: str) -> Dict[str, Any]:
        """Get detailed artist metadata"""
        try:
            artist = self.spotify_client.artist(artist_id)
            
            metadata = {
                'artist_id': artist.get('id'),
                'name': artist.get('name'),
                'popularity': artist.get('popularity', 0),
                'followers': artist.get('followers', {}).get('total', 0),
                'genres': artist.get('genres', []),
                'image_url': artist.get('images', [{}])[0].get('url', '') if artist.get('images') else ''
            }
            
            # Get top tracks
            top_tracks = self.spotify_client.artist_top_tracks(artist_id)
            metadata['top_tracks'] = []
            
            for track in top_tracks.get('tracks', []):
                track_data = await self._process_single_track(track)
                metadata['top_tracks'].append(track_data)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error getting artist metadata: {str(e)}")
            return {}
    
    async def _get_playlist_metadata(self, playlist_id: str) -> Dict[str, Any]:
        """Get detailed playlist metadata"""
        try:
            return await self.analyze_playlist(playlist_id)
            
        except Exception as e:
            self.logger.error(f"Error getting playlist metadata: {str(e)}")
            return {}
    
    def _extract_spotify_id_from_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract Spotify ID and content type from URL"""
        try:
            # Pattern for Spotify URLs
            import re
            pattern = r'spotify\.com/(track|album|artist|playlist)/([a-zA-Z0-9]+)'
            match = re.search(pattern, url)
            
            if match:
                return match.group(2), match.group(1)
            
            # Try Spotify URI format
            uri_pattern = r'spotify:(track|album|artist|playlist):([a-zA-Z0-9]+)'
            uri_match = re.search(uri_pattern, url)
            
            if uri_match:
                return uri_match.group(2), uri_match.group(1)
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"Error extracting Spotify ID from URL: {str(e)}")
            return None, None
    
    def _parse_release_date(self, date_str: str) -> Optional[datetime]:
        """Parse Spotify release date"""
        if not date_str:
            return None
        
        try:
            # Spotify dates can be YYYY, YYYY-MM, or YYYY-MM-DD
            if len(date_str) == 4:  # Year only
                return datetime(int(date_str), 1, 1)
            elif len(date_str) == 7:  # Year-Month
                year, month = date_str.split('-')
                return datetime(int(year), int(month), 1)
            else:  # Full date
                return datetime.fromisoformat(date_str)
                
        except Exception as e:
            self.logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return None
    
    async def _calculate_average_audio_features(self, tracks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average audio features for a collection of tracks"""
        try:
            feature_keys = ['danceability', 'energy', 'speechiness', 'acousticness',
                          'instrumentalness', 'liveness', 'valence', 'tempo']
            
            averages = {}
            valid_tracks = []
            
            for track in tracks:
                if track.get('audio_features'):
                    valid_tracks.append(track['audio_features'])
            
            if not valid_tracks:
                return {}
            
            for key in feature_keys:
                values = [track.get(key, 0) for track in valid_tracks if track.get(key) is not None]
                if values:
                    averages[key] = sum(values) / len(values)
            
            return averages
            
        except Exception as e:
            self.logger.error(f"Error calculating average audio features: {str(e)}")
            return {}
    
    async def _check_rate_limit(self):
        """Check and manage API rate limits"""
        current_time = datetime.utcnow()
        
        # Reset window if needed
        if (current_time - self.window_start).total_seconds() >= self.rate_limit_window:
            self.current_requests = 0
            self.window_start = current_time
        
        # Check if we're approaching limit
        if self.current_requests >= self.requests_per_minute * 0.9:  # 90% of limit
            wait_time = self.rate_limit_window - (current_time - self.window_start).total_seconds()
            if wait_time > 0:
                self.logger.warning(f"Rate limit approaching, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                self.current_requests = 0
                self.window_start = datetime.utcnow()
    
    async def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate content from results"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            # Use appropriate ID based on content type
            content_id = (result.get('track_id') or 
                         result.get('album_id') or 
                         result.get('artist_id') or 
                         result.get('playlist_id'))
            
            if content_id and content_id not in seen_ids:
                seen_ids.add(content_id)
                unique_results.append(result)
        
        return unique_results
    
    async def _send_new_release_notification(self, album: Dict[str, Any], 
                                           callback_url: str, monitoring_id: str):
        """Send notification for new release"""
        try:
            notification_data = {
                'monitoring_id': monitoring_id,
                'platform': 'spotify',
                'content_type': 'new_release',
                'album_id': album.get('id'),
                'album_name': album.get('name'),
                'artists': [artist['name'] for artist in album.get('artists', [])],
                'release_date': album.get('release_date'),
                'total_tracks': album.get('total_tracks'),
                'url': album.get('external_urls', {}).get('spotify'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(callback_url, json=notification_data)
                
        except Exception as e:
            self.logger.error(f"Error sending new release notification: {str(e)}")
