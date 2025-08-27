"""
Spotify Agent - Ultra-Advanced Spotify Integration & Analytics System

Industrial-grade Spotify API integration providing comprehensive artist analytics, music recommendation,
playlist management, and automated marketing for musicians and content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy import stats

from ..base import BaseAgent, AgentRequest, AgentResponse, AgentStatus, AgentPriority
from .spotify_api import SpotifyAPIClient, AuthManager, SpotifyError
from .analytics_engine import StreamingAnalytics, AudienceInsights, TrendAnalyzer
from .playlist_manager import PlaylistManager, RecommendationEngine
from .artist_tools import ArtistProfileManager, ReleaseOptimizer
from ...core.config import settings
from ...core.database import get_db_session
from ...security.content_protection import ContentFingerprinter
from ...utils.caching import CacheManager
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class SpotifyFeature(Enum):
    """Available Spotify features for activation"""
    ANALYTICS = "analytics"
    PLAYLISTS = "playlists"
    RECOMMENDATIONS = "recommendations"
    ARTIST_TOOLS = "artist_tools"
    TREND_ANALYSIS = "trend_analysis"
    AUDIENCE_INSIGHTS = "audience_insights"
    RELEASE_OPTIMIZATION = "release_optimization"
    COLLABORATIVE_FILTERING = "collaborative_filtering"

class MarketRegion(Enum):
    """Supported market regions for analytics"""
    GLOBAL = "global"
    US = "US"
    UK = "GB"
    GERMANY = "DE"
    FRANCE = "FR"
    CANADA = "CA"
    AUSTRALIA = "AU"
    JAPAN = "JP"
    BRAZIL = "BR"
    MEXICO = "MX"

@dataclass
class SpotifyArtistProfile:
    """Comprehensive artist profile data structure"""
    artist_id: str
    name: str
    genres: List[str] = field(default_factory=list)
    followers: int = 0
    popularity: int = 0
    external_urls: Dict[str, str] = field(default_factory=dict)
    images: List[Dict[str, Any]] = field(default_factory=list)
    monthly_listeners: int = 0
    total_streams: int = 0
    top_tracks: List[Dict[str, Any]] = field(default_factory=list)
    albums: List[Dict[str, Any]] = field(default_factory=list)
    related_artists: List[str] = field(default_factory=list)
    markets: List[str] = field(default_factory=list)
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class StreamingMetrics:
    """Advanced streaming performance metrics"""
    track_id: str
    streams_total: int = 0
    streams_daily: int = 0
    streams_weekly: int = 0
    streams_monthly: int = 0
    skip_rate: float = 0.0
    completion_rate: float = 0.0
    saves: int = 0
    shares: int = 0
    playlist_adds: int = 0
    discovery_rate: float = 0.0
    viral_coefficient: float = 0.0
    engagement_score: float = 0.0
    peak_position: Optional[int] = None
    chart_performance: Dict[str, Any] = field(default_factory=dict)
    demographic_breakdown: Dict[str, Any] = field(default_factory=dict)

class SpotifyAgent(BaseAgent):
    """
    Ultra-Advanced Spotify Integration Agent
    
    Provides comprehensive Spotify API integration with advanced analytics,
    machine learning-powered recommendations, and automated music marketing capabilities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Spotify Agent with advanced configuration"""
        super().__init__(
            agent_type="spotify_agent",
            version="2.1.0",
            config=config or {}
        )
        
        # Core components
        self.auth_manager = AuthManager(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scopes=self._get_required_scopes()
        )
        
        self.api_client = SpotifyAPIClient(self.auth_manager)
        self.analytics_engine = StreamingAnalytics()
        self.audience_insights = AudienceInsights()
        self.trend_analyzer = TrendAnalyzer()
        self.playlist_manager = PlaylistManager(self.api_client)
        self.recommendation_engine = RecommendationEngine()
        self.artist_profile_manager = ArtistProfileManager(self.api_client)
        self.release_optimizer = ReleaseOptimizer()
        
        # Advanced features
        self.cache_manager = CacheManager(prefix="spotify_agent")
        self.performance_monitor = PerformanceMonitor("spotify_agent")
        self.content_fingerprinter = ContentFingerprinter()
        
        # Configuration
        self.enabled_features = set(self.config.get("enabled_features", [f.value for f in SpotifyFeature]))
        self.default_market = MarketRegion(self.config.get("default_market", "global"))
        self.analytics_window_days = self.config.get("analytics_window_days", 30)
        self.recommendation_limit = self.config.get("recommendation_limit", 50)
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hour
        
        # Machine learning models
        self.feature_scaler = StandardScaler()
        self.similarity_model = None
        self.trend_prediction_model = None
        
        logger.info(f"Spotify Agent initialized with features: {self.enabled_features}")

    def _get_required_scopes(self) -> List[str]:
        """Get required Spotify API scopes based on enabled features"""
        base_scopes = [
            "user-read-email",
            "user-read-private",
            "user-library-read",
            "user-top-read",
            "user-read-recently-played",
            "user-follow-read",
            "playlist-read-private",
            "playlist-read-collaborative"
        ]
        
        write_scopes = [
            "playlist-modify-public",
            "playlist-modify-private",
            "user-library-modify",
            "user-follow-modify"
        ]
        
        streaming_scopes = [
            "streaming",
            "user-read-playback-state",
            "user-modify-playback-state"
        ]
        
        # Add scopes based on enabled features
        if SpotifyFeature.PLAYLISTS.value in self.enabled_features:
            base_scopes.extend(write_scopes)
        
        if "streaming_control" in self.config.get("advanced_features", []):
            base_scopes.extend(streaming_scopes)
            
        return list(set(base_scopes))

    async def authenticate_user(self, user_id: str, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user with Spotify and store tokens"""
        try:
            if auth_code:
                # Exchange authorization code for tokens
                tokens = await self.auth_manager.exchange_code_for_tokens(auth_code)
            else:
                # Get existing tokens or refresh
                tokens = await self.auth_manager.get_user_tokens(user_id)
                
            if not tokens:
                # Generate authorization URL for new authentication
                auth_url = self.auth_manager.get_authorization_url(user_id)
                return {
                    "authenticated": False,
                    "authorization_url": auth_url,
                    "message": "User needs to authorize Spotify access"
                }
            
            # Validate tokens and refresh if needed
            valid_tokens = await self.auth_manager.validate_and_refresh_tokens(user_id, tokens)
            
            # Get user profile to confirm authentication
            user_profile = await self.api_client.get_current_user_profile(valid_tokens["access_token"])
            
            return {
                "authenticated": True,
                "user_profile": user_profile,
                "expires_at": valid_tokens["expires_at"],
                "scopes": valid_tokens.get("scope", "").split()
            }
            
        except SpotifyError as e:
            logger.error(f"Spotify authentication failed for user {user_id}: {e}")
            raise ProcessingError(f"Authentication failed: {e}")

    async def get_artist_analytics(self, artist_id: str, time_range: str = "medium_term", 
                                 market: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive artist analytics and insights"""
        if SpotifyFeature.ANALYTICS.value not in self.enabled_features:
            raise ValidationError("Analytics feature not enabled")
        
        cache_key = f"artist_analytics:{artist_id}:{time_range}:{market or 'global'}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get basic artist information
            artist_info = await self.api_client.get_artist(artist_id)
            
            # Get top tracks with detailed audio features
            top_tracks = await self.api_client.get_artist_top_tracks(artist_id, market)
            
            # Analyze audio features for all tracks
            track_ids = [track["id"] for track in top_tracks["tracks"]]
            audio_features = await self.api_client.get_audio_features(track_ids)
            
            # Get streaming analytics
            streaming_metrics = await self.analytics_engine.get_artist_streaming_data(
                artist_id, time_range, market
            )
            
            # Get audience insights
            audience_data = await self.audience_insights.analyze_artist_audience(
                artist_id, time_range
            )
            
            # Perform trend analysis
            trend_data = await self.trend_analyzer.analyze_artist_trends(
                artist_id, self.analytics_window_days
            )
            
            # Calculate advanced metrics
            advanced_metrics = await self._calculate_advanced_artist_metrics(
                artist_info, top_tracks, audio_features, streaming_metrics
            )
            
            analytics_data = {
                "artist_info": artist_info,
                "streaming_metrics": streaming_metrics,
                "audience_insights": audience_data,
                "trend_analysis": trend_data,
                "top_tracks_analysis": self._analyze_top_tracks(top_tracks, audio_features),
                "advanced_metrics": advanced_metrics,
                "market_analysis": await self._get_market_performance(artist_id, market),
                "competitive_analysis": await self._get_competitive_insights(artist_id),
                "optimization_recommendations": await self._generate_optimization_recommendations(
                    artist_info, streaming_metrics, trend_data
                ),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_range": time_range,
                "market": market or "global"
            }
            
            # Cache results
            await self.cache_manager.set(cache_key, analytics_data, ttl=self.cache_ttl)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to get artist analytics for {artist_id}: {e}")
            raise ProcessingError(f"Analytics generation failed: {e}")

    async def get_track_recommendations(self, seed_data: Dict[str, Any], 
                                      limit: int = 20, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate AI-powered track recommendations using advanced algorithms"""
        if SpotifyFeature.RECOMMENDATIONS.value not in self.enabled_features:
            raise ValidationError("Recommendations feature not enabled")
        
        try:
            # Extract seed parameters
            seed_tracks = seed_data.get("seed_tracks", [])
            seed_artists = seed_data.get("seed_artists", [])
            seed_genres = seed_data.get("seed_genres", [])
            target_features = seed_data.get("target_audio_features", {})
            
            # Validate seed data
            total_seeds = len(seed_tracks) + len(seed_artists) + len(seed_genres)
            if total_seeds == 0 or total_seeds > 5:
                raise ValidationError("Total seeds must be between 1 and 5")
            
            # Get basic Spotify recommendations
            spotify_recommendations = await self.api_client.get_recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists, 
                seed_genres=seed_genres,
                target_features=target_features,
                limit=min(limit * 2, 100),  # Get more to filter/rank
                market=market
            )
            
            # Enhance recommendations with ML-powered ranking
            enhanced_recommendations = await self.recommendation_engine.enhance_recommendations(
                spotify_recommendations["tracks"],
                seed_data,
                user_preferences=seed_data.get("user_preferences", {})
            )
            
            # Apply content-based filtering
            filtered_recommendations = await self._apply_content_filtering(
                enhanced_recommendations,
                seed_data.get("content_filters", {})
            )
            
            # Add detailed track analysis
            analyzed_recommendations = []
            for track in filtered_recommendations[:limit]:
                track_analysis = await self._analyze_recommended_track(track, seed_data)
                analyzed_recommendations.append({
                    **track,
                    "recommendation_score": track_analysis["score"],
                    "similarity_reasons": track_analysis["reasons"],
                    "audio_analysis": track_analysis["audio_features"],
                    "match_confidence": track_analysis["confidence"]
                })
            
            return analyzed_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise ProcessingError(f"Recommendation generation failed: {e}")

    async def create_optimized_playlist(self, playlist_data: Dict[str, Any], 
                                      user_access_token: str) -> Dict[str, Any]:
        """Create an AI-optimized playlist with advanced curation"""
        if SpotifyFeature.PLAYLISTS.value not in self.enabled_features:
            raise ValidationError("Playlist feature not enabled")
        
        try:
            # Extract playlist parameters
            name = playlist_data["name"]
            description = playlist_data.get("description", "")
            public = playlist_data.get("public", True)
            collaborative = playlist_data.get("collaborative", False)
            optimization_goals = playlist_data.get("optimization_goals", [])
            
            # Create base playlist
            playlist = await self.playlist_manager.create_playlist(
                name=name,
                description=description,
                public=public,
                collaborative=collaborative,
                access_token=user_access_token
            )
            
            # Generate optimized track selection
            if "tracks" in playlist_data:
                # Use provided tracks
                tracks = playlist_data["tracks"]
            else:
                # Generate tracks based on criteria
                tracks = await self._generate_playlist_tracks(
                    playlist_data.get("criteria", {}),
                    playlist_data.get("target_length", 50)
                )
            
            # Optimize track order using advanced algorithms
            optimized_tracks = await self.playlist_manager.optimize_track_order(
                tracks, 
                goals=optimization_goals
            )
            
            # Add tracks to playlist in batches
            batch_size = 100
            for i in range(0, len(optimized_tracks), batch_size):
                batch = optimized_tracks[i:i + batch_size]
                track_uris = [f"spotify:track:{track['id']}" for track in batch]
                await self.playlist_manager.add_tracks_to_playlist(
                    playlist["id"], 
                    track_uris,
                    user_access_token
                )
            
            # Generate playlist analytics
            playlist_analytics = await self._analyze_playlist_composition(
                optimized_tracks, optimization_goals
            )
            
            return {
                "playlist": playlist,
                "track_count": len(optimized_tracks),
                "optimization_applied": optimization_goals,
                "analytics": playlist_analytics,
                "estimated_duration": sum(track.get("duration_ms", 0) for track in optimized_tracks) / 1000,
                "genre_distribution": self._calculate_genre_distribution(optimized_tracks),
                "energy_profile": self._calculate_energy_profile(optimized_tracks),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create optimized playlist: {e}")
            raise ProcessingError(f"Playlist creation failed: {e}")

    async def analyze_release_timing(self, track_data: Dict[str, Any], 
                                   artist_id: str) -> Dict[str, Any]:
        """Analyze optimal release timing using advanced ML algorithms"""
        if SpotifyFeature.RELEASE_OPTIMIZATION.value not in self.enabled_features:
            raise ValidationError("Release optimization feature not enabled")
        
        try:
            # Get historical performance data
            historical_data = await self.analytics_engine.get_artist_release_history(
                artist_id, days=365
            )
            
            # Analyze seasonal trends
            seasonal_analysis = await self.trend_analyzer.analyze_seasonal_patterns(
                historical_data, artist_id
            )
            
            # Get competitive landscape
            competitive_data = await self._analyze_release_competition(
                track_data, seasonal_analysis["optimal_periods"]
            )
            
            # Perform audience behavior analysis
            audience_behavior = await self.audience_insights.analyze_listening_patterns(
                artist_id
            )
            
            # Generate ML-powered timing recommendations
            timing_recommendations = await self.release_optimizer.optimize_release_timing(
                track_data=track_data,
                historical_performance=historical_data,
                seasonal_patterns=seasonal_analysis,
                competitive_landscape=competitive_data,
                audience_behavior=audience_behavior
            )
            
            # Calculate success probability for different timing scenarios
            success_probabilities = await self._calculate_release_success_probabilities(
                timing_recommendations, historical_data
            )
            
            return {
                "optimal_release_dates": timing_recommendations["primary_recommendations"],
                "alternative_dates": timing_recommendations["alternative_options"],
                "success_probabilities": success_probabilities,
                "seasonal_insights": seasonal_analysis,
                "competitive_analysis": competitive_data,
                "audience_readiness": audience_behavior["engagement_trends"],
                "marketing_recommendations": await self._generate_marketing_timeline(
                    timing_recommendations["primary_recommendations"][0]
                ),
                "risk_factors": timing_recommendations.get("risk_factors", []),
                "confidence_score": timing_recommendations.get("confidence", 0.0),
                "analysis_date": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Release timing analysis failed: {e}")
            raise ProcessingError(f"Release timing analysis failed: {e}")

    async def get_audience_insights(self, artist_id: str, time_range: str = "medium_term") -> Dict[str, Any]:
        """Generate comprehensive audience insights and demographics"""
        if SpotifyFeature.AUDIENCE_INSIGHTS.value not in self.enabled_features:
            raise ValidationError("Audience insights feature not enabled")
        
        cache_key = f"audience_insights:{artist_id}:{time_range}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get detailed audience analytics
            audience_data = await self.audience_insights.get_comprehensive_audience_data(
                artist_id, time_range
            )
            
            # Analyze listener behavior patterns
            behavior_patterns = await self.audience_insights.analyze_listener_behavior(
                artist_id, time_range
            )
            
            # Generate demographic breakdowns
            demographics = await self.audience_insights.get_demographic_breakdown(
                artist_id, time_range
            )
            
            # Analyze geographic distribution
            geographic_data = await self.audience_insights.analyze_geographic_distribution(
                artist_id, time_range
            )
            
            # Calculate engagement metrics
            engagement_metrics = await self.audience_insights.calculate_engagement_metrics(
                artist_id, audience_data, behavior_patterns
            )
            
            # Generate audience growth predictions
            growth_predictions = await self._predict_audience_growth(
                audience_data, behavior_patterns, demographics
            )
            
            # Identify audience segments
            audience_segments = await self.audience_insights.segment_audience(
                audience_data, demographics, behavior_patterns
            )
            
            insights_data = {
                "audience_overview": audience_data,
                "behavior_patterns": behavior_patterns,
                "demographics": demographics,
                "geographic_distribution": geographic_data,
                "engagement_metrics": engagement_metrics,
                "audience_segments": audience_segments,
                "growth_predictions": growth_predictions,
                "retention_analysis": await self._analyze_audience_retention(artist_id),
                "discovery_sources": await self._analyze_discovery_sources(artist_id),
                "playlist_performance": await self._analyze_playlist_performance(artist_id),
                "fan_loyalty_index": engagement_metrics.get("loyalty_score", 0.0),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_range": time_range
            }
            
            # Cache results
            await self.cache_manager.set(cache_key, insights_data, ttl=self.cache_ttl)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate audience insights for {artist_id}: {e}")
            raise ProcessingError(f"Audience insights generation failed: {e}")

    async def _calculate_advanced_artist_metrics(self, artist_info: Dict[str, Any],
                                               top_tracks: Dict[str, Any], 
                                               audio_features: List[Dict[str, Any]],
                                               streaming_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced artist performance metrics"""
        try:
            # Audio feature analysis
            feature_analysis = self._analyze_audio_features(audio_features)
            
            # Popularity trends
            popularity_trend = await self._calculate_popularity_trend(
                artist_info["id"], streaming_metrics
            )
            
            # Genre consistency analysis
            genre_consistency = self._analyze_genre_consistency(
                artist_info["genres"], top_tracks["tracks"]
            )
            
            # Market penetration analysis
            market_penetration = await self._analyze_market_penetration(
                artist_info["id"], streaming_metrics
            )
            
            # Viral potential calculation
            viral_potential = self._calculate_viral_potential(
                streaming_metrics, feature_analysis
            )
            
            return {
                "audio_signature": feature_analysis,
                "popularity_trend": popularity_trend,
                "genre_consistency_score": genre_consistency,
                "market_penetration": market_penetration,
                "viral_potential_score": viral_potential,
                "discoverability_index": self._calculate_discoverability_index(
                    artist_info, feature_analysis, streaming_metrics
                ),
                "fan_engagement_score": streaming_metrics.get("engagement_score", 0.0),
                "career_momentum": self._calculate_career_momentum(streaming_metrics),
                "commercial_appeal": self._calculate_commercial_appeal(
                    audio_features, streaming_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"Advanced metrics calculation failed: {e}")
            return {}

    def _analyze_audio_features(self, audio_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audio features to create artist signature"""
        if not audio_features:
            return {}
        
        features = [f for f in audio_features if f is not None]
        if not features:
            return {}
        
        # Calculate average values for each feature
        feature_keys = ["acousticness", "danceability", "energy", "instrumentalness", 
                       "liveness", "loudness", "speechiness", "valence", "tempo"]
        
        averages = {}
        variations = {}
        
        for key in feature_keys:
            values = [f.get(key, 0) for f in features if f.get(key) is not None]
            if values:
                averages[key] = np.mean(values)
                variations[key] = np.std(values)
        
        # Calculate signature characteristics
        signature = {
            "primary_mood": self._determine_primary_mood(averages),
            "energy_level": self._categorize_energy_level(averages.get("energy", 0)),
            "musical_complexity": self._calculate_complexity_score(averages, variations),
            "commercial_potential": self._assess_commercial_potential(averages),
            "uniqueness_score": self._calculate_uniqueness_score(variations)
        }
        
        return {
            "feature_averages": averages,
            "feature_variations": variations,
            "signature_characteristics": signature
        }

    def _determine_primary_mood(self, features: Dict[str, float]) -> str:
        """Determine the primary mood based on audio features"""
        valence = features.get("valence", 0.5)
        energy = features.get("energy", 0.5)
        
        if valence > 0.6 and energy > 0.6:
            return "upbeat_happy"
        elif valence > 0.6 and energy < 0.4:
            return "chill_positive"
        elif valence < 0.4 and energy > 0.6:
            return "intense_dramatic"
        elif valence < 0.4 and energy < 0.4:
            return "melancholic_calm"
        else:
            return "neutral_balanced"

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process Spotify agent requests with comprehensive error handling"""
        try:
            action = request.action.lower()
            
            if action == "authenticate":
                result = await self.authenticate_user(
                    request.data.get("user_id"),
                    request.data.get("auth_code")
                )
            elif action == "get_artist_analytics":
                result = await self.get_artist_analytics(
                    request.data["artist_id"],
                    request.data.get("time_range", "medium_term"),
                    request.data.get("market")
                )
            elif action == "get_recommendations":
                result = await self.get_track_recommendations(
                    request.data["seed_data"],
                    request.data.get("limit", 20),
                    request.data.get("market")
                )
            elif action == "create_playlist":
                result = await self.create_optimized_playlist(
                    request.data["playlist_data"],
                    request.data["user_access_token"]
                )
            elif action == "analyze_release_timing":
                result = await self.analyze_release_timing(
                    request.data["track_data"],
                    request.data["artist_id"]
                )
            elif action == "get_audience_insights":
                result = await self.get_audience_insights(
                    request.data["artist_id"],
                    request.data.get("time_range", "medium_term")
                )
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "processing_time": time.time() - request.metadata.get("start_time", time.time()),
                    "agent_version": self.version,
                    "features_used": list(self.enabled_features)
                }
            )
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code=type(e).__name__
            )

class SpotifyAgentManager:
    """Manager for Spotify agent instances with advanced orchestration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, SpotifyAgent] = {}
        self.performance_monitor = PerformanceMonitor("spotify_agent_manager")
        
    async def get_agent(self, tenant_id: str) -> SpotifyAgent:
        """Get or create Spotify agent for tenant"""
        if tenant_id not in self.agents:
            tenant_config = await self._get_tenant_config(tenant_id)
            self.agents[tenant_id] = SpotifyAgent(tenant_config)
        
        return self.agents[tenant_id]
    
    async def _get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant-specific configuration"""
        # Implementation would fetch from database
        return self.config
