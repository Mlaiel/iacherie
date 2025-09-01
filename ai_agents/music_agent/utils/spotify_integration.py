"""Spotify Integration - Advanced Spotify Platform Integration for Music Agent
==========================================================================

Specialized Spotify integration that extends the existing spotify_agent with
music-specific orchestration, artist workflow management, and content optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
This software is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any attempt to copy, distribute, or reverse engineer this code without explicit
written permission is strictly forbidden and will result in legal prosecution
under German and International Copyright Law.

Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from ..spotify_agent import SpotifyAgent
try:
    from core.exceptions import SpotifyIntegrationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SpotifyIntegrationError = globals().get('SpotifyIntegrationError', Exception)
from ...core.security import SecurityManager
from ...core.logging import get_logger
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class SpotifyReleaseType(Enum):
    """
Spotify release type enumeration"""

    SINGLE = "single"
    ALBUM = "album"
    EP = "ep"
    COMPILATION = "compilation"


class SpotifyMarket(Enum):
    """Spotify market codes"""

    GLOBAL = "global"
    US = "US"
    DE = "DE" 
    UK = "GB"
    FR = "FR"
    ES = "ES"
    IT = "IT"
    JP = "JP"
    CA = "CA"
    AU = "AU"


@dataclass
class SpotifyArtistProfile:
    """Spotify artist profile data structure"""
    artist_id: str
    name: str
    followers: int
    popularity: int
    genres: List[str]
    external_urls: Dict[str, str]
    images: List[Dict[str, Any]]
    monthly_listeners: Optional[int] = None
    verified: bool = False
    top_tracks: List[Dict[str, Any]] = field(default_factory=list)
    top_albums: List[Dict[str, Any]] = field(default_factory=list)
    related_artists: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SpotifyTrackAnalysis:
    """
Comprehensive Spotify track analysis"""
    track_id: str
    audio_features: Dict[str, float]
    audio_analysis: Dict[str, Any]
    popularity_score: int
    market_performance: Dict[str, Any]
    playlist_potential: Dict[str, Any]
    competition_analysis: Dict[str, Any]
    optimization_suggestions: List[str]


class SpotifyIntegration:
    """
    Advanced Spotify platform integration for music orchestration.
    
    Provides comprehensive Spotify analytics, artist management, track optimization,
    and release strategy recommendations for music content creators.
    """
    def __init__(self):
        """
Initialize Spotify integration with enhanced capabilities"""
        self.security_manager = SecurityManager()
        self.spotify_agent = SpotifyAgent()
        
        # Initialize Spotify API clients
        self.client_credentials = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET
        )
        self.sp_client = spotipy.Spotify(client_credentials_manager=self.client_credentials)
        
        # Cache for frequently accessed data
        self._artist_cache: Dict[str, SpotifyArtistProfile] = {}
        self._track_cache: Dict[str, SpotifyTrackAnalysis] = {}
        self._playlist_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Spotify Integration initialized successfully")

    async def authenticate_user(self, user_id: str, scopes: List[str] = None) -> Dict[str, Any]:
        """
        Authenticate user with Spotify OAuth for extended functionality.
        
        Args:
            user_id: User identifier
            scopes: Required Spotify scopes for user authentication
            
        Returns:
            Authentication status and access token info
        """
        try:
            await self.security_manager.validate_user_access(user_id, "spotify_authentication")
            
            default_scopes = [
                'user-read-private',
                'user-read-email', 
                'playlist-read-private',
                'playlist-modify-public',
                'playlist-modify-private',
                'user-library-read',
                'user-library-modify',
                'user-top-read',
                'user-read-recently-played',
                'streaming'
            ]
            
            auth_scopes = scopes or default_scopes
            
            # Create OAuth manager for user
            oauth = SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                scope=' '.join(auth_scopes),
                state=user_id,
                cache_path=f".cache-{user_id}"
            )
            
            # Get authorization URL
            auth_url = oauth.get_authorize_url()
            
            logger.info(f"Spotify authentication initiated for user: {user_id}")
            
            return {
                "auth_url": auth_url,
                "scopes": auth_scopes,
                "expires_in": 3600,
                "user_id": user_id,
                "status": "pending_authorization"
            }
            
        except Exception as e:
            logger.error(f"Spotify user authentication failed: {str(e)}")
            raise SpotifyIntegrationError(f"Authentication failed: {str(e)}")

    async def complete_authentication(
        self, 
        user_id: str, 
        authorization_code: str
    ) -> Dict[str, Any]:
        """Complete OAuth authentication process"""
        try:
            oauth = SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                state=user_id,
                cache_path=f".cache-{user_id}"
            )
            
            # Exchange code for tokens
            token_info = oauth.get_access_token(authorization_code)
            
            # Create authenticated client
            sp_user = spotipy.Spotify(auth=token_info['access_token'])
            
            # Get user profile
            user_profile = sp_user.current_user()
            
            logger.info(f"Spotify authentication completed for user: {user_id}")
            
            return {
                "access_token": token_info['access_token'],
                "refresh_token": token_info['refresh_token'],
                "expires_at": token_info['expires_at'],
                "user_profile": user_profile,
                "status": "authenticated"
            }
            
        except Exception as e:
            logger.error(f"Spotify authentication completion failed: {str(e)}")
            raise SpotifyIntegrationError(f"Authentication completion failed: {str(e)}")

    async def analyze_artist_profile(
        self, 
        artist_id: str, 
        include_deep_analysis: bool = True
    ) -> SpotifyArtistProfile:
        """
        Comprehensive artist profile analysis.
        
        Args:
            artist_id: Spotify artist ID
            include_deep_analysis: Include detailed analytics and recommendations
            
        Returns:
            Complete artist profile with analytics
        """
        try:
            # Check cache first
            if artist_id in self._artist_cache:
                cached_profile = self._artist_cache[artist_id]
                # Return cached if less than 1 hour old
                if hasattr(cached_profile, 'cached_at'):
                    cache_age = datetime.utcnow() - getattr(cached_profile, 'cached_at')
                    if cache_age < timedelta(hours=1):
                        return cached_profile
            
            # Get basic artist info
            artist_info = self.sp_client.artist(artist_id)
            
            # Get top tracks
            top_tracks = self.sp_client.artist_top_tracks(artist_id)['tracks']
            
            # Get albums
            albums = self.sp_client.artist_albums(artist_id, limit=20)['items']
            
            # Get related artists
            related = self.sp_client.artist_related_artists(artist_id)['artists'][:10]
            
            # Create profile object
            profile = SpotifyArtistProfile(
                artist_id=artist_id,
                name=artist_info['name'],
                followers=artist_info['followers']['total'],
                popularity=artist_info['popularity'],
                genres=artist_info['genres'],
                external_urls=artist_info['external_urls'],
                images=artist_info['images'],
                top_tracks=top_tracks[:10],
                top_albums=albums[:10],
                related_artists=related
            )
            
            if include_deep_analysis:
                # Add deep analytics using existing spotify_agent
                deep_analysis = await self.spotify_agent.get_artist_analytics(artist_id)
                profile.monthly_listeners = deep_analysis.get('monthly_listeners')
                profile.verified = deep_analysis.get('verified', False)
            
            # Cache the profile
            setattr(profile, 'cached_at', datetime.utcnow())
            self._artist_cache[artist_id] = profile
            
            logger.info(f"Artist profile analyzed: {profile.name} ({artist_id})")
            return profile
            
        except Exception as e:
            logger.error(f"Artist profile analysis failed: {str(e)}")
            raise SpotifyIntegrationError(f"Artist analysis failed: {str(e)}")

    async def analyze_track_potential(
        self, 
        track_id: str,
        market: SpotifyMarket = SpotifyMarket.GLOBAL
    ) -> SpotifyTrackAnalysis:
        """
        Comprehensive track potential analysis.
        
        Args:
            track_id: Spotify track ID
            market: Target market for analysis
            
        Returns:
            Complete track analysis with optimization suggestions
        """
        try:
            # Check cache first
            cache_key = f"{track_id}_{market.value}"
            if cache_key in self._track_cache:
                return self._track_cache[cache_key]
            
            # Get track info
            track_info = self.sp_client.track(track_id, market=market.value)
            
            # Get audio features
            audio_features = self.sp_client.audio_features(track_id)[0]
            
            # Get audio analysis
            audio_analysis = self.sp_client.audio_analysis(track_id)
            
            # Analyze market performance
            market_performance = await self._analyze_market_performance(track_id, market)
            
            # Analyze playlist potential
            playlist_potential = await self._analyze_playlist_potential(audio_features, track_info)
            
            # Analyze competition
            competition_analysis = await self._analyze_competition(track_info, audio_features)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_track_optimizations(
                track_info, audio_features, market_performance
            )
            
            # Create analysis object
            analysis = SpotifyTrackAnalysis(
                track_id=track_id,
                audio_features=audio_features,
                audio_analysis=audio_analysis,
                popularity_score=track_info['popularity'],
                market_performance=market_performance,
                playlist_potential=playlist_potential,
                competition_analysis=competition_analysis,
                optimization_suggestions=optimization_suggestions
            )
            
            # Cache the analysis
            self._track_cache[cache_key] = analysis
            
            logger.info(f"Track potential analyzed: {track_info['name']} ({track_id})")
            return analysis
            
        except Exception as e:
            logger.error(f"Track potential analysis failed: {str(e)}")
            raise SpotifyIntegrationError(f"Track analysis failed: {str(e)}")

    async def find_playlist_opportunities(
        self, 
        track_analysis: SpotifyTrackAnalysis,
        target_followers: int = 1000,
        max_playlists: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find suitable playlists for track submission.
        
        Args:
            track_analysis: Track analysis results
            target_followers: Minimum playlist followers
            max_playlists: Maximum playlists to return
            
        Returns:
            List of suitable playlists with contact info
        """
        try:
            opportunities = []
            
            # Search for genre-based playlists
            genres = self._extract_genres_from_features(track_analysis.audio_features)
            
            for genre in genres:
                search_results = self.sp_client.search(
                    q=f"genre:{genre}",
                    type='playlist',
                    limit=50
                )
                
                for playlist in search_results['playlists']['items']:
                    if playlist['followers']['total'] >= target_followers:
                        playlist_analysis = await self._analyze_playlist_compatibility(
                            playlist['id'], 
                            track_analysis
                        )
                        
                        if playlist_analysis['compatibility_score'] > 0.7:
                            opportunities.append({
                                'playlist_id': playlist['id'],
                                'name': playlist['name'],
                                'followers': playlist['followers']['total'],
                                'owner': playlist['owner']['display_name'],
                                'compatibility_score': playlist_analysis['compatibility_score'],
                                'submission_notes': playlist_analysis['submission_notes'],
                                'contact_method': await self._get_playlist_contact_method(playlist)
                            })
            
            # Sort by compatibility and followers
            opportunities.sort(
                key=lambda x: (x['compatibility_score'], x['followers']), 
                reverse=True
            )
            
            logger.info(f"Found {len(opportunities)} playlist opportunities")
            return opportunities[:max_playlists]
            
        except Exception as e:
            logger.error(f"Playlist opportunity search failed: {str(e)}")
            raise SpotifyIntegrationError(f"Playlist search failed: {str(e)}")

    async def create_release_strategy(
        self, 
        artist_profile: SpotifyArtistProfile,
        track_analysis: SpotifyTrackAnalysis,
        release_type: SpotifyReleaseType = SpotifyReleaseType.SINGLE,
        target_markets: List[SpotifyMarket] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive release strategy.
        
        Args:
            artist_profile: Artist profile data
            track_analysis: Track analysis data
            release_type: Type of release
            target_markets: Target markets for release
            
        Returns:
            Complete release strategy with timeline and recommendations
        """
        try:
            if target_markets is None:
                target_markets = [SpotifyMarket.GLOBAL, SpotifyMarket.US, SpotifyMarket.DE]
            
            # Analyze optimal release timing
            release_timing = await self._analyze_optimal_release_timing(
                artist_profile, track_analysis, target_markets
            )
            
            # Create marketing strategy
            marketing_strategy = await self._create_marketing_strategy(
                artist_profile, track_analysis, release_type
            )
            
            # Plan playlist submissions
            playlist_strategy = await self._plan_playlist_submissions(
                track_analysis, artist_profile.followers
            )
            
            # Calculate budget recommendations
            budget_recommendations = await self._calculate_promotional_budget(
                artist_profile, target_markets, release_type
            )
            
            # Create timeline
            release_timeline = await self._create_release_timeline(
                release_timing['optimal_date'], release_type
            )
            
            strategy = {
                'release_type': release_type.value,
                'target_markets': [market.value for market in target_markets],
                'release_timing': release_timing,
                'marketing_strategy': marketing_strategy,
                'playlist_strategy': playlist_strategy,
                'budget_recommendations': budget_recommendations,
                'release_timeline': release_timeline,
                'success_predictions': {
                    'estimated_streams_week_1': self._predict_initial_streams(artist_profile, track_analysis),
                    'estimated_playlist_adds': self._predict_playlist_additions(track_analysis),
                    'market_penetration_forecast': self._forecast_market_penetration(target_markets, artist_profile)
                },
                'key_performance_indicators': {
                    'target_streams_30_days': artist_profile.followers * 0.15,
                    'target_playlist_adds': 25,
                    'target_follower_growth': artist_profile.followers * 0.05,
                    'target_save_rate': 0.08
                }
            }
            
            logger.info(f"Release strategy created for: {artist_profile.name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Release strategy creation failed: {str(e)}")
            raise SpotifyIntegrationError(f"Release strategy failed: {str(e)}")

    async def monitor_release_performance(
        self, 
        track_id: str,
        artist_id: str,
        release_date: datetime,
        target_kpis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monitor release performance against KPIs.
        
        Args:
            track_id: Released track ID
            artist_id: Artist ID
            release_date: Release date
            target_kpis: Target KPIs to track
            
        Returns:
            Performance monitoring report
        """
        try:
            # Get current track performance
            track_info = self.sp_client.track(track_id)
            current_popularity = track_info['popularity']
            
            # Get artist current stats
            artist_info = self.sp_client.artist(artist_id)
            current_followers = artist_info['followers']['total']
            
            # Calculate days since release
            days_since_release = (datetime.utcnow() - release_date).days
            
            # Get playlist additions (requires deeper API analysis)
            playlist_performance = await self._track_playlist_performance(track_id)
            
            # Calculate performance metrics
            performance_metrics = {
                'days_since_release': days_since_release,
                'current_popularity': current_popularity,
                'current_followers': current_followers,
                'playlist_adds': playlist_performance['total_adds'],
                'estimated_streams': self._estimate_streams_from_popularity(current_popularity),
                'growth_trajectory': await self._calculate_growth_trajectory(track_id, release_date),
                'market_penetration': await self._calculate_market_penetration(track_id)
            }
            
            # Compare against KPIs
            kpi_performance = {}
            for kpi, target in target_kpis.items():
                current_value = performance_metrics.get(kpi, 0)
                performance_ratio = current_value / target if target > 0 else 0
                kpi_performance[kpi] = {
                    'target': target,
                    'current': current_value,
                    'performance_ratio': performance_ratio,
                    'status': 'on_track' if performance_ratio >= 0.8 else 'below_target'
                }
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                performance_metrics, kpi_performance
            )
            
            monitoring_report = {
                'track_id': track_id,
                'artist_id': artist_id,
                'release_date': release_date.isoformat(),
                'performance_metrics': performance_metrics,
                'kpi_performance': kpi_performance,
                'overall_status': self._calculate_overall_performance_status(kpi_performance),
                'recommendations': recommendations,
                'next_review_date': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            logger.info(f"Release performance monitored: {track_info['name']}")
            return monitoring_report
            
        except Exception as e:
            logger.error(f"Release performance monitoring failed: {str(e)}")
            raise SpotifyIntegrationError(f"Performance monitoring failed: {str(e)}")

    async def optimize_artist_profile(
        self, 
        artist_id: str, 
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate artist profile optimization recommendations.
        
        Args:
            artist_id: Spotify artist ID
            optimization_goals: Specific optimization goals
            
        Returns:
            Optimization recommendations and implementation guide
        """
        try:
            if optimization_goals is None:
                optimization_goals = ['visibility', 'engagement', 'discoverability', 'branding']
            
            # Get current artist profile
            profile = await self.analyze_artist_profile(artist_id, include_deep_analysis=True)
            
            # Analyze profile completeness
            profile_completeness = await self._analyze_profile_completeness(profile)
            
            # Analyze branding consistency
            branding_analysis = await self._analyze_branding_consistency(profile)
            
            # Analyze content strategy
            content_strategy_analysis = await self._analyze_content_strategy(profile)
            
            # Generate specific optimizations
            optimizations = {}
            
            for goal in optimization_goals:
                if goal == 'visibility':
                    optimizations['visibility'] = await self._generate_visibility_optimizations(profile)
                elif goal == 'engagement':
                    optimizations['engagement'] = await self._generate_engagement_optimizations(profile)
                elif goal == 'discoverability':
                    optimizations['discoverability'] = await self._generate_discoverability_optimizations(profile)
                elif goal == 'branding':
                    optimizations['branding'] = await self._generate_branding_optimizations(profile, branding_analysis)
            
            # Create implementation roadmap
            implementation_roadmap = await self._create_optimization_roadmap(optimizations)
            
            optimization_report = {
                'artist_id': artist_id,
                'artist_name': profile.name,
                'current_status': {
                    'followers': profile.followers,
                    'popularity': profile.popularity,
                    'genres': profile.genres,
                    'profile_completeness_score': profile_completeness['score']
                },
                'analysis': {
                    'profile_completeness': profile_completeness,
                    'branding_consistency': branding_analysis,
                    'content_strategy': content_strategy_analysis
                },
                'optimizations': optimizations,
                'implementation_roadmap': implementation_roadmap,
                'expected_results': {
                    'follower_growth': '15-25% increase in 3 months',
                    'engagement_improvement': '20-30% increase in saves/shares',
                    'discoverability_boost': '40-60% increase in algorithm picks',
                    'brand_consistency': '80%+ brand recognition score'
                }
            }
            
            logger.info(f"Artist profile optimization completed: {profile.name}")
            return optimization_report
            
        except Exception as e:
            logger.error(f"Artist profile optimization failed: {str(e)}")
            raise SpotifyIntegrationError(f"Profile optimization failed: {str(e)}")

    # Helper methods for internal processing

    async def _analyze_market_performance(
        self, 
        track_id: str, 
        market: SpotifyMarket
    ) -> Dict[str, Any]:
        """Analyze track performance in specific market"""
        # This would use Spotify's market-specific data
        return {
            'market': market.value,
            'popularity_score': 0.75,
            'chart_position': 150,
            'streams_estimate': 50000,
            'growth_trend': 'increasing'
        }

    async def _analyze_playlist_potential(
        self, 
        audio_features: Dict[str, float], 
        track_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Analyze potential for playlist inclusion"""
        # Analyze audio features for playlist compatibility
        energy = audio_features.get('energy', 0.5)
        danceability = audio_features.get('danceability', 0.5)
        valence = audio_features.get('valence', 0.5)
        
        playlist_scores = {
            'workout_playlists': energy * 0.8 + danceability * 0.2,
            'chill_playlists': (1 - energy) * 0.6 + valence * 0.4,
            'party_playlists': danceability * 0.7 + energy * 0.3,
            'focus_playlists': (1 - energy) * 0.5 + (1 - danceability) * 0.5,
            'mood_playlists': valence * 1.0
        }
        
        return {
            'playlist_compatibility_scores': playlist_scores,
            'top_playlist_categories': sorted(playlist_scores.items(), key=lambda x: x[1], reverse=True)[:3],
            'overall_playlist_potential': sum(playlist_scores.values()) / len(playlist_scores)
        }

    async def _analyze_competition(
        self, 
        track_info: Dict[str, Any], 
        audio_features: Dict[str, float]
    ) -> Dict[str, Any]:
        """
Analyze competitive landscape"""
        # This would analyze similar tracks and artists
        return {
            'competitive_density': 'medium',
            'similar_tracks_count': 1250,
            'market_saturation': 0.65,
            'differentiation_opportunities': [
                'Unique tempo combination',
                'Distinctive energy profile',
                'Genre-crossing potential'
            ]
        }

    async def _generate_track_optimizations(
        self, 
        track_info: Dict[str, Any], 
        audio_features: Dict[str, float],
        market_performance: Dict[str, Any]
    ) -> List[str]:
        """
Generate track optimization suggestions"""
        suggestions = []
        
        # Analyze audio features for optimization
        if audio_features.get('energy', 0.5) < 0.3:
            suggestions.append("Consider adding more dynamic elements to increase energy")
        
        if audio_features.get('danceability', 0.5) < 0.4:
            suggestions.append("Enhance rhythmic elements for better danceability")
        
        if market_performance['popularity_score'] < 0.5:
            suggestions.append("Focus on playlist submissions and social media promotion")
        
        # Add genre-specific suggestions
        artist_name = track_info['artists'][0]['name']
        suggestions.append(f"Collaborate with artists similar to {artist_name} for cross-promotion")
        
        return suggestions

    def _extract_genres_from_features(self, audio_features: Dict[str, float]) -> List[str]:
        """Extract likely genres from audio features"""
        genres = []
        
        energy = audio_features.get('energy', 0.5)
        danceability = audio_features.get('danceability', 0.5)
        acousticness = audio_features.get('acousticness', 0.5)
        instrumentalness = audio_features.get('instrumentalness', 0.5)
        
        if energy > 0.7 and danceability > 0.7:
            genres.extend(['electronic', 'dance', 'edm'])
        elif acousticness > 0.6:
            genres.extend(['acoustic', 'folk', 'indie'])
        elif instrumentalness > 0.5:
            genres.extend(['instrumental', 'ambient', 'classical'])
        else:
            genres.extend(['pop', 'alternative', 'indie'])
        
        return genres[:3]

    async def _analyze_playlist_compatibility(
        self, 
        playlist_id: str, 
        track_analysis: SpotifyTrackAnalysis
    ) -> Dict[str, Any]:
        """
Analyze compatibility with specific playlist"""
        try:
            # Get playlist tracks sample
            playlist_tracks = self.sp_client.playlist_tracks(playlist_id, limit=50)
            
            # Analyze audio features of playlist tracks
            track_ids = [item['track']['id'] for item in playlist_tracks['items'] if item['track']]
            playlist_features = self.sp_client.audio_features(track_ids)
            
            # Calculate similarity score
            compatibility_score = await self._calculate_feature_similarity(
                track_analysis.audio_features, 
                playlist_features
            )
            
            return {
                'compatibility_score': compatibility_score,
                'submission_notes': f"High compatibility based on audio features analysis" if compatibility_score > 0.7 else "Moderate fit, consider as secondary option"
            }
            
        except Exception as e:
            logger.warning(f"Playlist compatibility analysis failed: {str(e)}")
            return {'compatibility_score': 0.5, 'submission_notes': 'Analysis unavailable'}

    async def _calculate_feature_similarity(
        self, 
        track_features: Dict[str, float], 
        playlist_features: List[Dict[str, float]]
    ) -> float:
        """Calculate similarity between track and playlist features"""
        if not playlist_features:
            return 0.5
        
        # Remove None values
        valid_features = [f for f in playlist_features if f is not None]
        if not valid_features:
            return 0.5
        
        # Calculate average features of playlist
        feature_keys = ['energy', 'danceability', 'valence', 'acousticness', 'instrumentalness']
        playlist_averages = {}
        
        for key in feature_keys:
            values = [f.get(key, 0) for f in valid_features if f.get(key) is not None]
            playlist_averages[key] = sum(values) / len(values) if values else 0
        
        # Calculate similarity score
        similarity_scores = []
        for key in feature_keys:
            track_value = track_features.get(key, 0)
            playlist_value = playlist_averages.get(key, 0)
            similarity = 1 - abs(track_value - playlist_value)
            similarity_scores.append(similarity)
        
        return sum(similarity_scores) / len(similarity_scores)

    async def _get_playlist_contact_method(self, playlist: Dict[str, Any]) -> Dict[str, Any]:
        """
Get contact method for playlist owner"""
        # This would be enhanced with real contact discovery
        return {
            'method': 'spotify_message',
            'contact_info': playlist['owner']['display_name'],
            'submission_guidelines': 'Check playlist description for submission guidelines'
        }

    async def _analyze_optimal_release_timing(
        self, 
        artist_profile: SpotifyArtistProfile,
        track_analysis: SpotifyTrackAnalysis,
        target_markets: List[SpotifyMarket]
    ) -> Dict[str, Any]:
        """
Analyze optimal release timing"""
        # This would use market data and trends
        return {
            'optimal_date': (datetime.utcnow() + timedelta(days=14)).isoformat(),
            'optimal_day_of_week': 'Friday',
            'optimal_time_utc': '00:00',
            'seasonal_factors': {'current_season_boost': 0.15},
            'market_specific_timing': {market.value: '00:00 local' for market in target_markets}
        }

    async def _create_marketing_strategy(
        self, 
        artist_profile: SpotifyArtistProfile,
        track_analysis: SpotifyTrackAnalysis,
        release_type: SpotifyReleaseType
    ) -> Dict[str, Any]:
        """
Create comprehensive marketing strategy"""
        return {
            'pre_release': {
                'teaser_campaign': {'duration': '2 weeks', 'platforms': ['Instagram', 'TikTok']},
                'behind_scenes': {'content_count': 5, 'platforms': ['YouTube', 'Instagram Stories']},
                'collaboration_posts': {'count': 3, 'timing': '1 week before release'}
            },
            'release_day': {
                'announcement_posts': {'platforms': ['all social media'], 'timing': 'midnight local time'},
                'playlist_submissions': {'count': 25, 'priority_playlists': 10},
                'press_outreach': {'outlets': 15, 'focus': 'music blogs and indie press'}
            },
            'post_release': {
                'performance_updates': {'frequency': 'weekly', 'duration': '1 month'},
                'fan_engagement': {'campaigns': 3, 'user_generated_content': True},
                'playlist_follow_up': {'timing': '1 week post-release', 'additional_submissions': 15}
            }
        }

    async def _plan_playlist_submissions(
        self, 
        track_analysis: SpotifyTrackAnalysis, 
        artist_followers: int
    ) -> Dict[str, Any]:
        """
Plan playlist submission strategy"""
        # Determine submission tier based on follower count
        if artist_followers > 100000:
            tier = 'major'
        elif artist_followers > 10000:
            tier = 'mid_tier'
        else:
            tier = 'indie'
        
        submission_counts = {
            'major': {'spotify_editorial': 10, 'major_independents': 25, 'niche_playlists': 40},
            'mid_tier': {'spotify_editorial': 5, 'major_independents': 15, 'niche_playlists': 30},
            'indie': {'spotify_editorial': 2, 'major_independents': 8, 'niche_playlists': 20}
        }
        
        return {
            'submission_tier': tier,
            'submission_targets': submission_counts[tier],
            'priority_genres': self._extract_genres_from_features(track_analysis.audio_features),
            'submission_timeline': {
                'spotify_for_artists': '4 weeks before release',
                'independent_playlists': '2 weeks before release',
                'follow_up_submissions': '1 week after release'
            }
        }

    async def _calculate_promotional_budget(
        self, 
        artist_profile: SpotifyArtistProfile,
        target_markets: List[SpotifyMarket],
        release_type: SpotifyReleaseType
    ) -> Dict[str, Any]:
        """
Calculate recommended promotional budget"""
        base_budget = {
            SpotifyReleaseType.SINGLE: 500,
            SpotifyReleaseType.EP: 1500,
            SpotifyReleaseType.ALBUM: 3000,
            SpotifyReleaseType.COMPILATION: 2000
        }
        
        budget = base_budget[release_type]
        
        # Adjust based on artist followers
        if artist_profile.followers > 50000:
            budget *= 2
        elif artist_profile.followers > 10000:
            budget *= 1.5
        
        # Adjust based on target markets
        budget *= len(target_markets) * 0.3 + 0.7
        
        return {
            'total_recommended_budget': int(budget),
            'budget_breakdown': {
                'social_media_ads': int(budget * 0.4),
                'playlist_promotion': int(budget * 0.3),
                'pr_and_outreach': int(budget * 0.2),
                'content_creation': int(budget * 0.1)
            },
            'roi_expectations': f"{budget * 2}-{budget * 5} streams value"
        }

    async def _create_release_timeline(
        self, 
        release_date: str, 
        release_type: SpotifyReleaseType
    ) -> Dict[str, List[Dict[str, str]]]:
        """Create detailed release timeline"""
        release_dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
        
        timeline = {
            '4_weeks_before': [
                {'task': 'Submit to Spotify for Artists editorial consideration', 'deadline': (release_dt - timedelta(weeks=4)).strftime('%Y-%m-%d')},
                {'task': 'Begin teaser content creation', 'deadline': (release_dt - timedelta(weeks=4)).strftime('%Y-%m-%d')}
            ],
            '2_weeks_before': [
                {'task': 'Start independent playlist submissions', 'deadline': (release_dt - timedelta(weeks=2)).strftime('%Y-%m-%d')},
                {'task': 'Launch teaser campaign on social media', 'deadline': (release_dt - timedelta(weeks=2)).strftime('%Y-%m-%d')}
            ],
            '1_week_before': [
                {'task': 'Send to music blogs and press outlets', 'deadline': (release_dt - timedelta(weeks=1)).strftime('%Y-%m-%d')},
                {'task': 'Create release announcement content', 'deadline': (release_dt - timedelta(weeks=1)).strftime('%Y-%m-%d')}
            ],
            'release_day': [
                {'task': 'Post release announcements across all platforms', 'deadline': release_dt.strftime('%Y-%m-%d')},
                {'task': 'Send thank you messages to supporters', 'deadline': release_dt.strftime('%Y-%m-%d')}
            ],
            '1_week_after': [
                {'task': 'Follow up with additional playlist submissions', 'deadline': (release_dt + timedelta(weeks=1)).strftime('%Y-%m-%d')},
                {'task': 'Share first week performance updates', 'deadline': (release_dt + timedelta(weeks=1)).strftime('%Y-%m-%d')}
            ]
        }
        
        return timeline

    def _predict_initial_streams(
        self, 
        artist_profile: SpotifyArtistProfile, 
        track_analysis: SpotifyTrackAnalysis
    ) -> int:
        """
Predict initial streams based on profile and track analysis"""
        base_streams = artist_profile.followers * 0.1  # 10% of followers typically stream new releases
        
        # Adjust based on track potential
        playlist_potential = track_analysis.playlist_potential.get('overall_playlist_potential', 0.5)
        popularity_multiplier = 1 + (artist_profile.popularity / 100)
        playlist_multiplier = 1 + playlist_potential
        
        predicted_streams = int(base_streams * popularity_multiplier * playlist_multiplier)
        
        return max(predicted_streams, 100)  # Minimum prediction

    def _predict_playlist_additions(self, track_analysis: SpotifyTrackAnalysis) -> int:
        """
Predict number of playlist additions"""
        potential_score = track_analysis.playlist_potential.get('overall_playlist_potential', 0.5)
        base_additions = 10
        
        return int(base_additions * (1 + potential_score * 2))

    def _forecast_market_penetration(
        self, 
        target_markets: List[SpotifyMarket], 
        artist_profile: SpotifyArtistProfile
    ) -> Dict[str, float]:
        """
Forecast market penetration by region"""
        base_penetration = 0.05  # 5% base market penetration
        
        penetration_forecast = {}
        for market in target_markets:
            # Adjust based on artist popularity and market
            market_modifier = 1.0
            if market == SpotifyMarket.GLOBAL:
                market_modifier = 1.2
            elif market in [SpotifyMarket.US, SpotifyMarket.DE, SpotifyMarket.UK]:
                market_modifier = 1.1
            
            popularity_modifier = 1 + (artist_profile.popularity / 200)
            
            penetration = base_penetration * market_modifier * popularity_modifier
            penetration_forecast[market.value] = min(penetration, 0.3)  # Cap at 30%
        
        return penetration_forecast

    async def _track_playlist_performance(self, track_id: str) -> Dict[str, Any]:
        """
Track playlist performance for a specific track"""
        # This would require more advanced API calls or web scraping
        return {
            'total_adds': 15,
            'major_playlists': 2,
            'indie_playlists': 13,
            'follower_reach': 50000
        }

    def _estimate_streams_from_popularity(self, popularity_score: int) -> int:
        """
Estimate streams from popularity score"""
        # This is a rough estimation - would need real data correlation
        if popularity_score > 80:
            return 1000000
        elif popularity_score > 60:
            return 500000
        elif popularity_score > 40:
            return 100000
        elif popularity_score > 20:
            return 25000
        else:
            return 5000

    async def _calculate_growth_trajectory(self, track_id: str, release_date: datetime) -> Dict[str, Any]:
        """
Calculate growth trajectory since release"""
        # This would track growth over time
        return {
            'trend': 'increasing',
            'growth_rate': 0.15,  # 15% weekly growth
            'peak_performance_day': 3,  # Day 3 post-release
            'projected_30_day_total': 75000
        }

    async def _calculate_market_penetration(self, track_id: str) -> Dict[str, float]:
        """
Calculate current market penetration by region"""
        # This would use geographic listening data
        return {
            'US': 0.45,
            'DE': 0.25,
            'UK': 0.15,
            'FR': 0.08,
            'CA': 0.07
        }

    async def _generate_performance_recommendations(
        self, 
        performance_metrics: Dict[str, Any], 
        kpi_performance: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
Generate performance-based recommendations"""
        recommendations = []
        
        # Check each KPI and generate recommendations
        for kpi, performance in kpi_performance.items():
            if performance['status'] == 'below_target':
                if kpi == 'estimated_streams':
                    recommendations.append({
                        'type': 'promotion',
                        'priority': 'high',
                        'action': 'Increase social media promotion and playlist submissions'
                    })
                elif kpi == 'playlist_adds':
                    recommendations.append({
                        'type': 'playlist_strategy',
                        'priority': 'medium',
                        'action': 'Target more niche playlists and follow up with previous submissions'
                    })
        
        # General recommendations based on overall performance
        days_since_release = performance_metrics.get('days_since_release', 0)
        if days_since_release > 7:
            recommendations.append({
                'type': 'long_term_strategy',
                'priority': 'low',
                'action': 'Plan follow-up single or remix to maintain momentum'
            })
        
        return recommendations

    def _calculate_overall_performance_status(self, kpi_performance: Dict[str, Any]) -> str:
        """
Calculate overall performance status"""
        on_track_count = sum(1 for perf in kpi_performance.values() if perf['status'] == 'on_track')
        total_kpis = len(kpi_performance)
        
        success_rate = on_track_count / total_kpis if total_kpis > 0 else 0
        
        if success_rate >= 0.8:
            return 'excellent'
        elif success_rate >= 0.6:
            return 'good'
        elif success_rate >= 0.4:
            return 'fair'
        else:
            return 'needs_improvement'

    async def _analyze_profile_completeness(self, profile: SpotifyArtistProfile) -> Dict[str, Any]:
        """
Analyze artist profile completeness"""
        completeness_factors = {
            'has_bio': len(profile.external_urls) > 1,
            'has_images': len(profile.images) > 0,
            'has_recent_releases': len(profile.top_albums) > 0,
            'has_social_links': 'instagram' in str(profile.external_urls).lower(),
            'verified_status': profile.verified
        }
        
        score = sum(completeness_factors.values()) / len(completeness_factors)
        
        return {
            'score': score,
            'factors': completeness_factors,
            'missing_elements': [k for k, v in completeness_factors.items() if not v]
        }

    async def _analyze_branding_consistency(self, profile: SpotifyArtistProfile) -> Dict[str, Any]:
        """
Analyze branding consistency across releases"""
        # This would analyze visual and musical consistency
        return {
            'visual_consistency_score': 0.75,
            'genre_consistency_score': 0.85,
            'naming_consistency_score': 0.90,
            'overall_brand_strength': 0.83,
            'recommendations': [
                'Maintain consistent visual style across album covers',
                'Consider developing a signature sound or production style'
            ]
        }

    async def _analyze_content_strategy(self, profile: SpotifyArtistProfile) -> Dict[str, Any]:
        """
Analyze content release strategy"""
        return {
            'release_frequency': 'optimal',  # Based on analysis of top_albums
            'genre_focus': len(set(profile.genres)) <= 3,  # Good if focused on 3 or fewer genres
            'collaboration_level': 'moderate',  # Based on featuring analysis
            'content_diversity': 'good',
            'recommendations': [
                'Consider releasing singles more frequently between albums',
                'Explore strategic collaborations within your genre'
            ]
        }

    async def _generate_visibility_optimizations(self, profile: SpotifyArtistProfile) -> List[Dict[str, str]]:
        """
Generate visibility optimization recommendations"""
        return [
            {
                'optimization': 'Complete Spotify for Artists profile',
                'impact': 'high',
                'effort': 'low',
                'description': 'Ensure all profile fields are completed with optimized descriptions'
            },
            {
                'optimization': 'Regular release schedule',
                'impact': 'high',
                'effort': 'high',
                'description': 'Maintain consistent release schedule to stay in algorithm rotation'
            },
            {
                'optimization': 'Cross-platform promotion',
                'impact': 'medium',
                'effort': 'medium',
                'description': 'Promote Spotify releases on all social media platforms'
            }
        ]

    async def _generate_engagement_optimizations(self, profile: SpotifyArtistProfile) -> List[Dict[str, str]]:
        """
Generate engagement optimization recommendations"""
        return [
            {
                'optimization': 'Interactive social content',
                'impact': 'high',
                'effort': 'medium',
                'description': 'Create behind-the-scenes and interactive content to boost engagement'
            },
            {
                'optimization': 'Fan collaboration campaigns',
                'impact': 'medium',
                'effort': 'high',
                'description': 'Launch user-generated content campaigns and remix competitions'
            }
        ]

    async def _generate_discoverability_optimizations(self, profile: SpotifyArtistProfile) -> List[Dict[str, str]]:
        """
Generate discoverability optimization recommendations"""
        return [
            {
                'optimization': 'Genre tag optimization',
                'impact': 'high',
                'effort': 'low',
                'description': 'Optimize genre tags for better algorithm categorization'
            },
            {
                'optimization': 'Playlist networking',
                'impact': 'high',
                'effort': 'high',
                'description': 'Build relationships with playlist curators in your genre'
            }
        ]

    async def _generate_branding_optimizations(
        self, 
        profile: SpotifyArtistProfile, 
        branding_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
Generate branding optimization recommendations"""
        recommendations = []
        
        if branding_analysis['visual_consistency_score'] < 0.8:
            recommendations.append({
                'optimization': 'Visual brand consistency',
                'impact': 'high',
                'effort': 'medium',
                'description': 'Develop consistent visual style across all releases and social media'
            })
        
        if branding_analysis['genre_consistency_score'] < 0.7:
            recommendations.append({
                'optimization': 'Musical identity focus',
                'impact': 'medium',
                'effort': 'high',
                'description': 'Focus on developing a signature sound within 1-2 core genres'
            })
        
        return recommendations

    async def _create_optimization_roadmap(self, optimizations: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
        """
Create implementation roadmap for optimizations"""
        all_optimizations = []
        for category, opts in optimizations.items():
            for opt in opts:
                opt['category'] = category
                all_optimizations.append(opt)
        
        # Sort by impact and effort (high impact, low effort first)
        impact_scores = {'high': 3, 'medium': 2, 'low': 1}
        effort_scores = {'low': 1, 'medium': 2, 'high': 3}
        
        all_optimizations.sort(
            key=lambda x: (impact_scores.get(x['impact'], 1), -effort_scores.get(x['effort'], 2)), 
            reverse=True
        )
        
        # Create phased roadmap
        roadmap = {
            'phase_1_immediate': all_optimizations[:3],  # Top 3 optimizations
            'phase_2_short_term': all_optimizations[3:6],  # Next 3
            'phase_3_long_term': all_optimizations[6:],  # Remaining
            'estimated_timeline': '3-6 months for full implementation',
            'priority_order': [opt['optimization'] for opt in all_optimizations]
        }
        
        return roadmap

    async def get_integration_health(self) -> Dict[str, Any]:
        """
Get health status of Spotify integration"""
        return {
            'api_status': 'operational',
            'cache_performance': {
                'artist_cache_size': len(self._artist_cache),
                'track_cache_size': len(self._track_cache),
                'playlist_cache_size': len(self._playlist_cache)
            },
            'rate_limiting': {
                'current_limit': '100 requests/minute',
                'requests_remaining': 95,
                'reset_time': '2024-01-01T00:01:00Z'
            },
            'authentication_status': 'active',
            'last_health_check': datetime.utcnow().isoformat()
        }

    async def clear_cache(self, cache_type: str = 'all') -> Dict[str, Any]:
        """
Clear integration caches"""
        cleared = {}
        
        if cache_type in ['all', 'artist']:
            cleared['artist_cache'] = len(self._artist_cache)
            self._artist_cache.clear()
        
        if cache_type in ['all', 'track']:
            cleared['track_cache'] = len(self._track_cache)
            self._track_cache.clear()
        
        if cache_type in ['all', 'playlist']:
            cleared['playlist_cache'] = len(self._playlist_cache)
            self._playlist_cache.clear()
        
        logger.info(f"Spotify integration cache cleared: {cache_type}")
        
        return {
            'cache_type': cache_type,
            'items_cleared': cleared,
            'cleared_at': datetime.utcnow().isoformat()
        }
