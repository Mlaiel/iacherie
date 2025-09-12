"""Spotify SEO Optimizer - Advanced Music Platform SEO Optimization
Comprehensive SEO optimization for Spotify including track metadata optimization,
playlist optimization, artist profile enhancement, and music discovery algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)


class SpotifyContentType(Enum):
    """Spotify content types"""
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST_PROFILE = "artist_profile"
    PODCAST = "podcast"
    EPISODE = "episode"


class MusicGenre(Enum):
    """Music genres for optimization"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    FOLK = "folk"
    REGGAE = "reggae"
    LATIN = "latin"
    WORLD = "world"
    AMBIENT = "ambient"


class SpotifyAudience(Enum):
    """Spotify audience segments"""
    YOUNG_ADULTS = "young_adults"  # 18-25
    MILLENNIALS = "millennials"    # 26-35
    GEN_X = "gen_x"               # 36-50
    MUSIC_ENTHUSIASTS = "music_enthusiasts"
    CASUAL_LISTENERS = "casual_listeners"
    COMMUTERS = "commuters"
    WORKOUT = "workout"
    STUDY = "study"
    PARTY = "party"
    CHILL = "chill"


@dataclass
class SpotifyTrackMetadata:
    """Spotify track metadata optimization"""
    title: str
    artist: str
    album: str
    genre: MusicGenre
    tags: List[str]
    description: str
    mood: str
    energy_level: float  # 0.0 to 1.0
    danceability: float  # 0.0 to 1.0
    valence: float      # 0.0 to 1.0 (positivity)
    tempo: int          # BPM
    duration_ms: int
    release_date: datetime
    isrc: Optional[str] = None
    explicit: bool = False


@dataclass
class SpotifyOptimization:
    """Spotify content optimization results"""
    original_metadata: Dict[str, Any]
    optimized_metadata: SpotifyTrackMetadata
    keyword_optimization: Dict[str, List[str]]
    playlist_recommendations: List[str]
    discovery_score: float
    searchability_score: float
    algorithmic_score: float
    mood_targeting: Dict[str, float]
    audience_targeting: List[SpotifyAudience]
    release_timing: datetime
    collaboration_suggestions: List[str] = field(default_factory=list)


@dataclass
class PlaylistOptimization:
    """Spotify playlist optimization"""
    title: str
    description: str
    cover_art_suggestions: List[str]
    track_order: List[str]
    genre_flow: List[MusicGenre]
    mood_progression: List[str]
    energy_curve: List[float]
    target_duration: int  # minutes
    follower_prediction: int
    viral_potential: float


@dataclass
class SpotifyAnalytics:
    """Spotify performance analytics"""
    streams: int
    listeners: int
    saves: int
    playlist_adds: int
    skip_rate: float
    completion_rate: float
    discovery_sources: Dict[str, int]
    geographic_distribution: Dict[str, int]
    demographic_breakdown: Dict[str, int]
    peak_listening_times: List[str]
    seasonal_performance: Dict[str, float]


@dataclass
class SpotifySEOScore:
    """Comprehensive Spotify SEO score"""
    overall_score: float
    metadata_score: float
    discoverability_score: float
    algorithmic_score: float
    engagement_score: float
    searchability_score: float
    playlist_potential_score: float
    improvements: List[str] = field(default_factory=list)
    growth_opportunities: List[str] = field(default_factory=list)


class SpotifySEOOptimizer:
    """Advanced Spotify SEO optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Spotify SEO optimizer
        
        Args:
            config: Configuration including API keys, genre data, trends
        """
        self.config = config
        self.genre_keywords = self._load_genre_keywords()
        self.mood_keywords = self._load_mood_keywords()
        self.trending_tags = []
        self.playlist_database = {}
        self.algorithm_weights = self._initialize_algorithm_weights()
        
    def _load_genre_keywords(self) -> Dict[MusicGenre, List[str]]:
        """Load genre-specific keywords for optimization"""
        return {
            MusicGenre.POP: ['catchy', 'mainstream', 'radio', 'chart', 'hit', 'commercial'],
            MusicGenre.ROCK: ['guitar', 'drums', 'band', 'live', 'energy', 'powerful'],
            MusicGenre.HIP_HOP: ['rap', 'beats', 'urban', 'street', 'flow', 'lyrics'],
            MusicGenre.ELECTRONIC: ['synth', 'digital', 'dance', 'club', 'EDM', 'techno'],
            MusicGenre.JAZZ: ['improvisation', 'smooth', 'sophisticated', 'classic', 'swing'],
            MusicGenre.CLASSICAL: ['orchestra', 'symphony', 'elegant', 'timeless', 'traditional'],
            MusicGenre.COUNTRY: ['acoustic', 'storytelling', 'rural', 'americana', 'folk'],
            MusicGenre.R_AND_B: ['soulful', 'smooth', 'vocals', 'groove', 'rhythm'],
            MusicGenre.INDIE: ['independent', 'alternative', 'unique', 'artistic', 'creative'],
            MusicGenre.ALTERNATIVE: ['experimental', 'non-mainstream', 'innovative', 'edgy'],
            MusicGenre.FOLK: ['acoustic', 'traditional', 'storytelling', 'authentic', 'cultural'],
            MusicGenre.REGGAE: ['caribbean', 'rhythm', 'island', 'relaxed', 'spiritual'],
            MusicGenre.LATIN: ['hispanic', 'spanish', 'tropical', 'cultural', 'festive'],
            MusicGenre.WORLD: ['ethnic', 'cultural', 'traditional', 'global', 'diverse'],
            MusicGenre.AMBIENT: ['atmospheric', 'meditative', 'peaceful', 'background', 'chill']
        }
    
    def _load_mood_keywords(self) -> Dict[str, List[str]]:
        """Load mood-specific keywords"""
        return {
            'happy': ['upbeat', 'joyful', 'positive', 'cheerful', 'energetic', 'bright'],
            'sad': ['melancholy', 'emotional', 'heartbreak', 'contemplative', 'somber'],
            'energetic': ['high-energy', 'pumping', 'intense', 'powerful', 'driving'],
            'chill': ['relaxed', 'laid-back', 'mellow', 'smooth', 'peaceful', 'calm'],
            'romantic': ['love', 'intimate', 'passionate', 'tender', 'emotional'],
            'motivational': ['inspiring', 'uplifting', 'empowering', 'determined', 'strong'],
            'party': ['celebration', 'fun', 'dancing', 'exciting', 'lively', 'festive'],
            'workout': ['motivation', 'intensity', 'power', 'drive', 'energy', 'pump'],
            'study': ['focus', 'concentration', 'background', 'instrumental', 'ambient'],
            'sleep': ['soothing', 'gentle', 'peaceful', 'quiet', 'meditative', 'calming']
        }
    
    def _initialize_algorithm_weights(self) -> Dict[str, float]:
        """Initialize Spotify algorithm weighting factors"""
        return {
            'completion_rate': 0.25,
            'skip_rate': 0.20,
            'saves': 0.15,
            'playlist_adds': 0.15,
            'shares': 0.10,
            'search_clicks': 0.10,
            'repeat_listens': 0.05
        }
    
    async def optimize_track(self, track_data: Dict[str, Any]) -> SpotifyOptimization:
        """Optimize a track for Spotify discovery and engagement
        
        Args:
            track_data: Track metadata and audio features
            
        Returns:
            Optimized track metadata and recommendations
        """
        try:
            # Parse current metadata
            current_metadata = await self._parse_track_metadata(track_data)
            
            # Analyze audio features
            audio_features = await self._analyze_audio_features(track_data)
            
            # Optimize metadata
            optimized_metadata = await self._optimize_track_metadata(
                current_metadata, audio_features
            )
            
            # Generate keyword optimization
            keyword_optimization = await self._optimize_keywords(
                optimized_metadata, audio_features
            )
            
            # Find playlist recommendations
            playlist_recommendations = await self._find_playlist_opportunities(
                optimized_metadata, audio_features
            )
            
            # Calculate discovery scores
            discovery_score = await self._calculate_discovery_score(
                optimized_metadata, audio_features
            )
            
            searchability_score = await self._calculate_searchability_score(
                optimized_metadata, keyword_optimization
            )
            
            algorithmic_score = await self._calculate_algorithmic_score(
                audio_features, optimized_metadata
            )
            
            # Mood and audience targeting
            mood_targeting = await self._analyze_mood_targeting(audio_features)
            audience_targeting = await self._identify_target_audiences(
                optimized_metadata, audio_features
            )
            
            # Optimal release timing
            release_timing = await self._determine_optimal_release_time(
                optimized_metadata.genre, audience_targeting
            )
            
            # Collaboration suggestions
            collaboration_suggestions = await self._suggest_collaborations(
                optimized_metadata, audio_features
            )
            
            return SpotifyOptimization(
                original_metadata=track_data,
                optimized_metadata=optimized_metadata,
                keyword_optimization=keyword_optimization,
                playlist_recommendations=playlist_recommendations,
                discovery_score=discovery_score,
                searchability_score=searchability_score,
                algorithmic_score=algorithmic_score,
                mood_targeting=mood_targeting,
                audience_targeting=audience_targeting,
                release_timing=release_timing,
                collaboration_suggestions=collaboration_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error optimizing track: {str(e)}")
            raise
    
    async def _parse_track_metadata(self, track_data: Dict[str, Any]) -> SpotifyTrackMetadata:
        """Parse and validate track metadata"""
        try:
            return SpotifyTrackMetadata(
                title=track_data.get('title', ''),
                artist=track_data.get('artist', ''),
                album=track_data.get('album', ''),
                genre=MusicGenre(track_data.get('genre', 'pop')),
                tags=track_data.get('tags', []),
                description=track_data.get('description', ''),
                mood=track_data.get('mood', 'neutral'),
                energy_level=float(track_data.get('energy', 0.5)),
                danceability=float(track_data.get('danceability', 0.5)),
                valence=float(track_data.get('valence', 0.5)),
                tempo=int(track_data.get('tempo', 120)),
                duration_ms=int(track_data.get('duration_ms', 180000)),
                release_date=datetime.fromisoformat(
                    track_data.get('release_date', datetime.now().isoformat())
                ),
                isrc=track_data.get('isrc'),
                explicit=track_data.get('explicit', False)
            )
            
        except Exception as e:
            logger.error(f"Error parsing track metadata: {str(e)}")
            raise
    
    async def _analyze_audio_features(self, track_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audio features for optimization"""
        try:
            # Extract or calculate audio features
            features = {
                'acousticness': float(track_data.get('acousticness', 0.5)),
                'danceability': float(track_data.get('danceability', 0.5)),
                'energy': float(track_data.get('energy', 0.5)),
                'instrumentalness': float(track_data.get('instrumentalness', 0.1)),
                'liveness': float(track_data.get('liveness', 0.1)),
                'loudness': float(track_data.get('loudness', -10.0)),
                'speechiness': float(track_data.get('speechiness', 0.1)),
                'tempo': float(track_data.get('tempo', 120.0)),
                'valence': float(track_data.get('valence', 0.5)),
                'duration_ms': float(track_data.get('duration_ms', 180000))
            }
            
            # Calculate derived features
            features['energy_valence_product'] = features['energy'] * features['valence']
            features['danceability_tempo_factor'] = features['danceability'] * (features['tempo'] / 120)
            features['mood_score'] = (features['valence'] * 0.6) + (features['energy'] * 0.4)
            
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing audio features: {str(e)}")
            return {}
    
    async def _optimize_track_metadata(self, 
                                     metadata: SpotifyTrackMetadata,
                                     audio_features: Dict[str, float]) -> SpotifyTrackMetadata:
        """Optimize track metadata for better discoverability"""
        try:
            optimized = metadata
            
            # Optimize title for searchability
            optimized.title = await self._optimize_track_title(
                metadata.title, metadata.genre, audio_features
            )
            
            # Optimize description
            optimized.description = await self._generate_optimized_description(
                metadata, audio_features
            )
            
            # Optimize tags
            optimized.tags = await self._optimize_track_tags(
                metadata, audio_features
            )
            
            # Optimize mood classification
            optimized.mood = await self._classify_optimal_mood(audio_features)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing track metadata: {str(e)}")
            return metadata
    
    async def _optimize_track_title(self, 
                                  title: str,
                                  genre: MusicGenre,
                                  audio_features: Dict[str, float]) -> str:
        """Optimize track title for search and discovery"""
        try:
            # Keep original title but add strategic elements if needed
            optimized_title = title
            
            # Add genre-specific keywords if title is too generic
            if len(title.split()) < 2:
                genre_keywords = self.genre_keywords.get(genre, [])
                if genre_keywords and not any(kw in title.lower() for kw in genre_keywords):
                    # Add subtle genre hint
                    if audio_features.get('energy', 0.5) > 0.7:
                        optimized_title = f"{title} (High Energy Mix)"
                    elif audio_features.get('acousticness', 0.5) > 0.7:
                        optimized_title = f"{title} (Acoustic Version)"
            
            return optimized_title
            
        except Exception as e:
            logger.error(f"Error optimizing track title: {str(e)}")
            return title
    
    async def _generate_optimized_description(self, 
                                            metadata: SpotifyTrackMetadata,
                                            audio_features: Dict[str, float]) -> str:
        """Generate SEO-optimized track description"""
        try:
            description_parts = []
            
            # Genre and style
            genre_keywords = self.genre_keywords.get(metadata.genre, [])
            if genre_keywords:
                description_parts.append(f"A {genre_keywords[0]} {metadata.genre.value} track")
            
            # Mood and energy
            mood = await self._classify_optimal_mood(audio_features)
            mood_keywords = self.mood_keywords.get(mood, [])
            if mood_keywords:
                description_parts.append(f"with {mood_keywords[0]} vibes")
            
            # Tempo and danceability
            if audio_features.get('danceability', 0) > 0.7:
                description_parts.append("perfect for dancing")
            elif audio_features.get('energy', 0) > 0.8:
                description_parts.append("high-energy and powerful")
            elif audio_features.get('valence', 0) > 0.7:
                description_parts.append("uplifting and positive")
            
            # Use context
            use_cases = await self._identify_use_cases(audio_features)
            if use_cases:
                description_parts.append(f"ideal for {', '.join(use_cases[:2])}")
            
            # Combine parts
            if description_parts:
                description = ". ".join(description_parts).capitalize() + "."
                
                # Add artist context if available
                if metadata.artist:
                    description = f"{description} By {metadata.artist}."
                
                return description
            
            return metadata.description or f"New {metadata.genre.value} track by {metadata.artist}"
            
        except Exception as e:
            logger.error(f"Error generating optimized description: {str(e)}")
            return metadata.description
    
    async def _optimize_track_tags(self, 
                                 metadata: SpotifyTrackMetadata,
                                 audio_features: Dict[str, float]) -> List[str]:
        """Optimize track tags for discoverability"""
        try:
            optimized_tags = list(metadata.tags)
            
            # Add genre-specific tags
            genre_keywords = self.genre_keywords.get(metadata.genre, [])
            optimized_tags.extend(genre_keywords[:3])
            
            # Add mood tags
            mood = await self._classify_optimal_mood(audio_features)
            mood_keywords = self.mood_keywords.get(mood, [])
            optimized_tags.extend(mood_keywords[:2])
            
            # Add audio feature tags
            if audio_features.get('danceability', 0) > 0.7:
                optimized_tags.extend(['danceable', 'groove'])
            
            if audio_features.get('energy', 0) > 0.8:
                optimized_tags.extend(['high-energy', 'powerful'])
            
            if audio_features.get('acousticness', 0) > 0.7:
                optimized_tags.extend(['acoustic', 'organic'])
            
            if audio_features.get('instrumentalness', 0) > 0.7:
                optimized_tags.extend(['instrumental', 'no-vocals'])
            
            # Add use case tags
            use_cases = await self._identify_use_cases(audio_features)
            optimized_tags.extend(use_cases)
            
            # Remove duplicates and limit to optimal count
            optimized_tags = list(set(optimized_tags))[:15]  # Spotify optimal tag count
            
            return optimized_tags
            
        except Exception as e:
            logger.error(f"Error optimizing track tags: {str(e)}")
            return metadata.tags
    
    async def _classify_optimal_mood(self, audio_features: Dict[str, float]) -> str:
        """Classify optimal mood based on audio features"""
        try:
            valence = audio_features.get('valence', 0.5)
            energy = audio_features.get('energy', 0.5)
            danceability = audio_features.get('danceability', 0.5)
            
            # Mood classification logic
            if valence > 0.7 and energy > 0.7:
                return 'happy'
            elif valence > 0.6 and danceability > 0.7:
                return 'party'
            elif energy > 0.8:
                return 'energetic'
            elif valence < 0.3:
                return 'sad'
            elif energy < 0.3:
                return 'chill'
            elif danceability > 0.7:
                return 'party'
            elif valence > 0.6:
                return 'happy'
            else:
                return 'chill'
                
        except Exception as e:
            logger.error(f"Error classifying mood: {str(e)}")
            return 'neutral'
    
    async def _identify_use_cases(self, audio_features: Dict[str, float]) -> List[str]:
        """Identify optimal use cases for the track"""
        try:
            use_cases = []
            
            energy = audio_features.get('energy', 0.5)
            danceability = audio_features.get('danceability', 0.5)
            valence = audio_features.get('valence', 0.5)
            tempo = audio_features.get('tempo', 120)
            instrumentalness = audio_features.get('instrumentalness', 0.1)
            
            # Workout music
            if energy > 0.7 and tempo > 120:
                use_cases.append('workout')
            
            # Party music
            if danceability > 0.7 and energy > 0.6:
                use_cases.append('party')
            
            # Chill/relaxation
            if energy < 0.4 and valence > 0.3:
                use_cases.append('chill')
            
            # Study music
            if instrumentalness > 0.5 and energy < 0.6:
                use_cases.append('study')
            
            # Sleep/meditation
            if energy < 0.3 and tempo < 100:
                use_cases.append('sleep')
            
            # Driving music
            if energy > 0.6 and tempo > 110:
                use_cases.append('driving')
            
            # Focus music
            if instrumentalness > 0.3 and energy < 0.7:
                use_cases.append('focus')
            
            return use_cases[:3]  # Return top 3 use cases
            
        except Exception as e:
            logger.error(f"Error identifying use cases: {str(e)}")
            return []
    
    async def _optimize_keywords(self, 
                               metadata: SpotifyTrackMetadata,
                               audio_features: Dict[str, float]) -> Dict[str, List[str]]:
        """Optimize keywords for search and discovery"""
        try:
            keyword_optimization = {
                'primary_keywords': [],
                'secondary_keywords': [],
                'long_tail_keywords': [],
                'seasonal_keywords': [],
                'trending_keywords': []
            }
            
            # Primary keywords (genre + mood)
            genre_keywords = self.genre_keywords.get(metadata.genre, [])
            keyword_optimization['primary_keywords'].extend(genre_keywords[:3])
            
            mood = await self._classify_optimal_mood(audio_features)
            mood_keywords = self.mood_keywords.get(mood, [])
            keyword_optimization['primary_keywords'].extend(mood_keywords[:2])
            
            # Secondary keywords (audio features)
            if audio_features.get('danceability', 0) > 0.7:
                keyword_optimization['secondary_keywords'].extend(['dance', 'groove', 'rhythm'])
            
            if audio_features.get('energy', 0) > 0.8:
                keyword_optimization['secondary_keywords'].extend(['energetic', 'powerful', 'intense'])
            
            # Long-tail keywords (specific combinations)
            use_cases = await self._identify_use_cases(audio_features)
            for use_case in use_cases:
                keyword_optimization['long_tail_keywords'].append(
                    f"{metadata.genre.value} {use_case} music"
                )
                keyword_optimization['long_tail_keywords'].append(
                    f"{mood} {use_case} songs"
                )
            
            # Seasonal keywords
            current_month = datetime.now().month
            if current_month in [12, 1, 2]:  # Winter
                keyword_optimization['seasonal_keywords'].extend(['winter', 'cozy', 'holiday'])
            elif current_month in [3, 4, 5]:  # Spring
                keyword_optimization['seasonal_keywords'].extend(['spring', 'fresh', 'renewal'])
            elif current_month in [6, 7, 8]:  # Summer
                keyword_optimization['seasonal_keywords'].extend(['summer', 'sunshine', 'vacation'])
            else:  # Fall
                keyword_optimization['seasonal_keywords'].extend(['autumn', 'fall', 'nostalgic'])
            
            # Trending keywords (would be fetched from real data)
            keyword_optimization['trending_keywords'] = await self._get_trending_keywords()
            
            return keyword_optimization
            
        except Exception as e:
            logger.error(f"Error optimizing keywords: {str(e)}")
            return {}
    
    async def _find_playlist_opportunities(self, 
                                         metadata: SpotifyTrackMetadata,
                                         audio_features: Dict[str, float]) -> List[str]:
        """Find playlist placement opportunities"""
        try:
            playlist_opportunities = []
            
            # Genre-based playlists
            genre = metadata.genre.value
            playlist_opportunities.extend([
                f"Best {genre.title()} Songs",
                f"New {genre.title()} Music",
                f"{genre.title()} Hits",
                f"Indie {genre.title()}"
            ])
            
            # Mood-based playlists
            mood = await self._classify_optimal_mood(audio_features)
            playlist_opportunities.extend([
                f"{mood.title()} Music",
                f"{mood.title()} Vibes",
                f"Songs for {mood.title()} Moods"
            ])
            
            # Use case playlists
            use_cases = await self._identify_use_cases(audio_features)
            for use_case in use_cases:
                playlist_opportunities.extend([
                    f"{use_case.title()} Music",
                    f"Best {use_case.title()} Songs",
                    f"Ultimate {use_case.title()} Playlist"
                ])
            
            # Time-based playlists
            energy = audio_features.get('energy', 0.5)
            if energy > 0.7:
                playlist_opportunities.extend([
                    "Morning Energy", "Afternoon Pump", "High Energy Hits"
                ])
            elif energy < 0.4:
                playlist_opportunities.extend([
                    "Evening Chill", "Late Night Vibes", "Peaceful Moments"
                ])
            
            # Seasonal playlists
            current_month = datetime.now().month
            if current_month in [12, 1, 2]:
                playlist_opportunities.extend(["Winter Warmth", "Cozy Night In"])
            elif current_month in [6, 7, 8]:
                playlist_opportunities.extend(["Summer Vibes", "Beach Party"])
            
            return playlist_opportunities[:10]  # Return top 10 opportunities
            
        except Exception as e:
            logger.error(f"Error finding playlist opportunities: {str(e)}")
            return []
    
    async def _calculate_discovery_score(self, 
                                       metadata: SpotifyTrackMetadata,
                                       audio_features: Dict[str, float]) -> float:
        """Calculate discovery potential score"""
        try:
            score = 0.0
            
            # Metadata completeness (0.3 weight)
            metadata_completeness = 0.0
            if metadata.title:
                metadata_completeness += 0.2
            if metadata.description:
                metadata_completeness += 0.2
            if metadata.tags:
                metadata_completeness += 0.3
            if metadata.genre:
                metadata_completeness += 0.3
            
            score += metadata_completeness * 0.3
            
            # Audio feature optimization (0.4 weight)
            audio_score = 0.0
            
            # Optimal song length (3-4 minutes is ideal)
            duration_minutes = metadata.duration_ms / 60000
            if 2.5 <= duration_minutes <= 4.5:
                audio_score += 0.25
            elif 2.0 <= duration_minutes <= 5.0:
                audio_score += 0.15
            
            # Energy and valence balance
            energy = audio_features.get('energy', 0.5)
            valence = audio_features.get('valence', 0.5)
            if 0.4 <= energy <= 0.8 and 0.3 <= valence <= 0.8:
                audio_score += 0.25
            
            # Danceability for broad appeal
            danceability = audio_features.get('danceability', 0.5)
            if danceability > 0.5:
                audio_score += 0.2
            
            # Not too experimental
            if audio_features.get('instrumentalness', 0) < 0.5:
                audio_score += 0.15
            
            # Speech content balance
            if audio_features.get('speechiness', 0) < 0.33:
                audio_score += 0.15
            
            score += audio_score * 0.4
            
            # Genre popularity (0.2 weight)
            genre_popularity = {
                MusicGenre.POP: 0.9,
                MusicGenre.HIP_HOP: 0.85,
                MusicGenre.ELECTRONIC: 0.8,
                MusicGenre.ROCK: 0.75,
                MusicGenre.R_AND_B: 0.7,
                MusicGenre.INDIE: 0.65,
                MusicGenre.COUNTRY: 0.6,
                MusicGenre.JAZZ: 0.5,
                MusicGenre.CLASSICAL: 0.4,
                MusicGenre.FOLK: 0.45,
                MusicGenre.REGGAE: 0.55,
                MusicGenre.LATIN: 0.75,
                MusicGenre.WORLD: 0.4,
                MusicGenre.AMBIENT: 0.35,
                MusicGenre.ALTERNATIVE: 0.6
            }
            
            score += genre_popularity.get(metadata.genre, 0.5) * 0.2
            
            # Trend alignment (0.1 weight)
            # This would be based on current musical trends
            score += 0.7 * 0.1  # Assume good trend alignment
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating discovery score: {str(e)}")
            return 0.5
    
    async def _calculate_searchability_score(self, 
                                           metadata: SpotifyTrackMetadata,
                                           keyword_optimization: Dict[str, List[str]]) -> float:
        """Calculate searchability score"""
        try:
            score = 0.0
            
            # Title optimization (0.4 weight)
            title_score = 0.0
            if metadata.title:
                # Title length (not too short, not too long)
                if 5 <= len(metadata.title) <= 50:
                    title_score += 0.4
                
                # Contains searchable words
                searchable_words = sum(1 for word in metadata.title.split() if len(word) > 2)
                title_score += min(0.4, searchable_words * 0.1)
                
                # Not all caps or weird formatting
                if not metadata.title.isupper() and not metadata.title.islower():
                    title_score += 0.2
            
            score += title_score * 0.4
            
            # Tag optimization (0.3 weight)
            tag_score = 0.0
            if metadata.tags:
                # Optimal tag count
                if 5 <= len(metadata.tags) <= 15:
                    tag_score += 0.4
                
                # Tag diversity
                unique_categories = set()
                for tag in metadata.tags:
                    if any(genre_word in tag.lower() for genre_words in self.genre_keywords.values() for genre_word in genre_words):
                        unique_categories.add('genre')
                    if any(mood_word in tag.lower() for mood_words in self.mood_keywords.values() for mood_word in mood_words):
                        unique_categories.add('mood')
                
                tag_score += len(unique_categories) * 0.2
                
                # No duplicate concepts
                if len(set(metadata.tags)) == len(metadata.tags):
                    tag_score += 0.2
            
            score += tag_score * 0.3
            
            # Keyword optimization (0.2 weight)
            keyword_score = 0.0
            total_keywords = sum(len(keywords) for keywords in keyword_optimization.values())
            if total_keywords > 0:
                keyword_score = min(1.0, total_keywords / 20)  # Optimal around 20 keywords
            
            score += keyword_score * 0.2
            
            # Genre specificity (0.1 weight)
            genre_score = 0.8 if metadata.genre else 0.0
            score += genre_score * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating searchability score: {str(e)}")
            return 0.5
    
    async def _calculate_algorithmic_score(self, 
                                         audio_features: Dict[str, float],
                                         metadata: SpotifyTrackMetadata) -> float:
        """Calculate algorithmic recommendation score"""
        try:
            score = 0.0
            
            # Audio feature optimization for algorithm (0.6 weight)
            audio_score = 0.0
            
            # Spotify algorithm preferences
            energy = audio_features.get('energy', 0.5)
            danceability = audio_features.get('danceability', 0.5)
            valence = audio_features.get('valence', 0.5)
            
            # Moderate to high energy preferred
            if 0.4 <= energy <= 0.9:
                audio_score += 0.25
            
            # Good danceability
            if danceability > 0.5:
                audio_score += 0.2
            
            # Positive valence generally preferred
            if valence > 0.4:
                audio_score += 0.15
            
            # Optimal song length for completion rates
            duration_minutes = metadata.duration_ms / 60000
            if 2.5 <= duration_minutes <= 4.0:
                audio_score += 0.2
            elif 2.0 <= duration_minutes <= 5.0:
                audio_score += 0.1
            
            # Not too instrumental (unless that's the intent)
            if audio_features.get('instrumentalness', 0) < 0.5:
                audio_score += 0.1
            
            # Not too much speech
            if audio_features.get('speechiness', 0) < 0.33:
                audio_score += 0.1
            
            score += audio_score * 0.6
            
            # Metadata completeness for algorithm (0.2 weight)
            metadata_score = 0.0
            if metadata.genre:
                metadata_score += 0.3
            if metadata.tags and len(metadata.tags) >= 5:
                metadata_score += 0.4
            if metadata.description:
                metadata_score += 0.3
            
            score += metadata_score * 0.2
            
            # Genre algorithm preference (0.1 weight)
            algorithm_genre_preference = {
                MusicGenre.POP: 0.9,
                MusicGenre.HIP_HOP: 0.85,
                MusicGenre.ELECTRONIC: 0.8,
                MusicGenre.R_AND_B: 0.75,
                MusicGenre.INDIE: 0.7,
                MusicGenre.ROCK: 0.65,
                MusicGenre.LATIN: 0.8,
                MusicGenre.COUNTRY: 0.6,
                MusicGenre.JAZZ: 0.5,
                MusicGenre.CLASSICAL: 0.4,
                MusicGenre.FOLK: 0.45,
                MusicGenre.REGGAE: 0.55,
                MusicGenre.WORLD: 0.4,
                MusicGenre.AMBIENT: 0.35,
                MusicGenre.ALTERNATIVE: 0.6
            }
            
            score += algorithm_genre_preference.get(metadata.genre, 0.5) * 0.1
            
            # Freshness bonus (0.1 weight)
            days_since_release = (datetime.now() - metadata.release_date).days
            freshness_score = max(0, 1 - (days_since_release / 365))  # Decay over year
            score += freshness_score * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating algorithmic score: {str(e)}")
            return 0.5
    
    async def _analyze_mood_targeting(self, audio_features: Dict[str, float]) -> Dict[str, float]:
        """Analyze mood targeting potential"""
        try:
            mood_scores = {}
            
            valence = audio_features.get('valence', 0.5)
            energy = audio_features.get('energy', 0.5)
            danceability = audio_features.get('danceability', 0.5)
            
            # Calculate mood affinity scores
            mood_scores['happy'] = (valence * 0.7) + (energy * 0.3)
            mood_scores['sad'] = (1 - valence) * 0.8 + (1 - energy) * 0.2
            mood_scores['energetic'] = energy
            mood_scores['chill'] = (1 - energy) * 0.6 + (valence * 0.4)
            mood_scores['party'] = (danceability * 0.5) + (energy * 0.3) + (valence * 0.2)
            mood_scores['romantic'] = (valence * 0.4) + ((1 - energy) * 0.3) + (danceability * 0.3)
            mood_scores['workout'] = (energy * 0.6) + (danceability * 0.4)
            mood_scores['study'] = (1 - energy) * 0.5 + audio_features.get('instrumentalness', 0) * 0.5
            mood_scores['sleep'] = (1 - energy) * 0.7 + (1 - audio_features.get('loudness', 0) / 60) * 0.3
            
            # Normalize scores
            max_score = max(mood_scores.values()) if mood_scores.values() else 1
            mood_scores = {mood: score / max_score for mood, score in mood_scores.items()}
            
            return mood_scores
            
        except Exception as e:
            logger.error(f"Error analyzing mood targeting: {str(e)}")
            return {}
    
    async def _identify_target_audiences(self, 
                                       metadata: SpotifyTrackMetadata,
                                       audio_features: Dict[str, float]) -> List[SpotifyAudience]:
        """Identify target audience segments"""
        try:
            audiences = []
            
            energy = audio_features.get('energy', 0.5)
            danceability = audio_features.get('danceability', 0.5)
            valence = audio_features.get('valence', 0.5)
            
            # Age-based targeting
            if metadata.genre in [MusicGenre.HIP_HOP, MusicGenre.ELECTRONIC, MusicGenre.POP]:
                if energy > 0.7:
                    audiences.append(SpotifyAudience.YOUNG_ADULTS)
                else:
                    audiences.append(SpotifyAudience.MILLENNIALS)
            elif metadata.genre in [MusicGenre.ROCK, MusicGenre.ALTERNATIVE]:
                audiences.append(SpotifyAudience.MILLENNIALS)
                if energy > 0.6:
                    audiences.append(SpotifyAudience.YOUNG_ADULTS)
            elif metadata.genre in [MusicGenre.JAZZ, MusicGenre.CLASSICAL, MusicGenre.FOLK]:
                audiences.append(SpotifyAudience.GEN_X)
                audiences.append(SpotifyAudience.MUSIC_ENTHUSIASTS)
            
            # Activity-based targeting
            if energy > 0.8 and danceability > 0.7:
                audiences.append(SpotifyAudience.WORKOUT)
                audiences.append(SpotifyAudience.PARTY)
            elif energy < 0.3:
                audiences.append(SpotifyAudience.STUDY)
                if valence > 0.5:
                    audiences.append(SpotifyAudience.CHILL)
            elif danceability > 0.7:
                audiences.append(SpotifyAudience.PARTY)
            
            # General listening patterns
            if energy > 0.5 and valence > 0.5:
                audiences.append(SpotifyAudience.COMMUTERS)
            
            if 0.3 <= energy <= 0.7:
                audiences.append(SpotifyAudience.CASUAL_LISTENERS)
            
            # Remove duplicates
            return list(set(audiences))
            
        except Exception as e:
            logger.error(f"Error identifying target audiences: {str(e)}")
            return [SpotifyAudience.CASUAL_LISTENERS]
    
    async def _determine_optimal_release_time(self, 
                                            genre: MusicGenre,
                                            audiences: List[SpotifyAudience]) -> datetime:
        """Determine optimal release timing"""
        try:
            # Base optimal release time (Friday 12 AM EST is Spotify standard)
            base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Find next Friday
            days_until_friday = (4 - base_time.weekday()) % 7
            if days_until_friday == 0 and base_time.hour > 0:
                days_until_friday = 7
            
            optimal_date = base_time + timedelta(days=days_until_friday)
            
            # Adjust for specific genres and audiences
            if genre in [MusicGenre.ELECTRONIC, MusicGenre.HIP_HOP]:
                # These genres perform well on Friday nights
                optimal_date = optimal_date.replace(hour=21)  # 9 PM
            elif genre in [MusicGenre.CLASSICAL, MusicGenre.JAZZ]:
                # More mature audiences, Sunday morning
                optimal_date = optimal_date + timedelta(days=2)
                optimal_date = optimal_date.replace(hour=10)  # 10 AM Sunday
            elif SpotifyAudience.YOUNG_ADULTS in audiences:
                # Young adults active late
                optimal_date = optimal_date.replace(hour=23)  # 11 PM Friday
            
            return optimal_date
            
        except Exception as e:
            logger.error(f"Error determining optimal release time: {str(e)}")
            return datetime.now() + timedelta(days=1)
    
    async def _suggest_collaborations(self, 
                                    metadata: SpotifyTrackMetadata,
                                    audio_features: Dict[str, float]) -> List[str]:
        """Suggest collaboration opportunities"""
        try:
            suggestions = []
            
            # Genre-based collaborations
            if metadata.genre == MusicGenre.HIP_HOP:
                suggestions.extend([
                    "Featured rapper for hook",
                    "Producer collaboration",
                    "Vocalist for chorus"
                ])
            elif metadata.genre == MusicGenre.ELECTRONIC:
                suggestions.extend([
                    "Vocalist for drop",
                    "DJ remix collaboration",
                    "Producer co-creation"
                ])
            elif metadata.genre == MusicGenre.POP:
                suggestions.extend([
                    "Duet partner",
                    "Songwriter collaboration",
                    "Producer partnership"
                ])
            
            # Audio feature-based suggestions
            if audio_features.get('instrumentalness', 0) > 0.7:
                suggestions.append("Add vocalist for mainstream appeal")
            
            if audio_features.get('energy', 0.5) > 0.8:
                suggestions.append("Collaborate with high-energy performer")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting collaborations: {str(e)}")
            return []
    
    async def _get_trending_keywords(self) -> List[str]:
        """Get current trending keywords"""
        # Mock trending keywords (would be fetched from real data)
        return ['viral', 'trending', 'new music', 'fresh', 'latest']
    
    async def optimize_playlist(self, playlist_data: Dict[str, Any]) -> PlaylistOptimization:
        """Optimize a Spotify playlist for discovery and engagement"""
        try:
            tracks = playlist_data.get('tracks', [])
            
            # Analyze playlist content
            playlist_analysis = await self._analyze_playlist_content(tracks)
            
            # Optimize title and description
            optimized_title = await self._optimize_playlist_title(
                playlist_data.get('title', ''), playlist_analysis
            )
            
            optimized_description = await self._optimize_playlist_description(
                playlist_analysis
            )
            
            # Generate cover art suggestions
            cover_art_suggestions = await self._suggest_cover_art(playlist_analysis)
            
            # Optimize track order
            optimized_track_order = await self._optimize_track_order(tracks)
            
            # Analyze genre flow
            genre_flow = await self._analyze_genre_flow(tracks)
            
            # Analyze mood progression
            mood_progression = await self._analyze_mood_progression(tracks)
            
            # Calculate energy curve
            energy_curve = await self._calculate_energy_curve(tracks)
            
            # Determine target duration
            target_duration = await self._calculate_optimal_duration(playlist_analysis)
            
            # Predict follower potential
            follower_prediction = await self._predict_followers(playlist_analysis)
            
            # Calculate viral potential
            viral_potential = await self._calculate_playlist_viral_potential(playlist_analysis)
            
            return PlaylistOptimization(
                title=optimized_title,
                description=optimized_description,
                cover_art_suggestions=cover_art_suggestions,
                track_order=optimized_track_order,
                genre_flow=genre_flow,
                mood_progression=mood_progression,
                energy_curve=energy_curve,
                target_duration=target_duration,
                follower_prediction=follower_prediction,
                viral_potential=viral_potential
            )
            
        except Exception as e:
            logger.error(f"Error optimizing playlist: {str(e)}")
            raise
    
    async def calculate_spotify_seo_score(self, track_data: Dict[str, Any]) -> SpotifySEOScore:
        """Calculate comprehensive Spotify SEO score"""
        try:
            # Parse metadata and features
            metadata = await self._parse_track_metadata(track_data)
            audio_features = await self._analyze_audio_features(track_data)
            
            # Calculate component scores
            metadata_score = await self._score_metadata_completeness(metadata)
            discoverability_score = await self._calculate_discovery_score(metadata, audio_features)
            algorithmic_score = await self._calculate_algorithmic_score(audio_features, metadata)
            engagement_score = await self._calculate_engagement_potential(audio_features)
            
            keyword_optimization = await self._optimize_keywords(metadata, audio_features)
            searchability_score = await self._calculate_searchability_score(metadata, keyword_optimization)
            
            playlist_potential_score = await self._calculate_playlist_potential(metadata, audio_features)
            
            # Calculate overall score
            weights = {
                'metadata': 0.15,
                'discoverability': 0.20,
                'algorithmic': 0.25,
                'engagement': 0.15,
                'searchability': 0.15,
                'playlist_potential': 0.10
            }
            
            overall_score = (
                metadata_score * weights['metadata'] +
                discoverability_score * weights['discoverability'] +
                algorithmic_score * weights['algorithmic'] +
                engagement_score * weights['engagement'] +
                searchability_score * weights['searchability'] +
                playlist_potential_score * weights['playlist_potential']
            )
            
            # Generate improvements and opportunities
            improvements = await self._generate_spotify_improvements(
                metadata_score, discoverability_score, algorithmic_score,
                engagement_score, searchability_score, playlist_potential_score
            )
            
            growth_opportunities = await self._identify_growth_opportunities(
                metadata, audio_features
            )
            
            return SpotifySEOScore(
                overall_score=overall_score,
                metadata_score=metadata_score,
                discoverability_score=discoverability_score,
                algorithmic_score=algorithmic_score,
                engagement_score=engagement_score,
                searchability_score=searchability_score,
                playlist_potential_score=playlist_potential_score,
                improvements=improvements,
                growth_opportunities=growth_opportunities
            )
            
        except Exception as e:
            logger.error(f"Error calculating Spotify SEO score: {str(e)}")
            raise
    
    # Additional helper methods would be implemented here...
    async def _score_metadata_completeness(self, metadata: SpotifyTrackMetadata) -> float:
        """Score metadata completeness"""
        score = 0.0
        if metadata.title: score += 0.2
        if metadata.description: score += 0.2
        if metadata.tags and len(metadata.tags) >= 5: score += 0.3
        if metadata.genre: score += 0.15
        if metadata.mood: score += 0.15
        return score
    
    async def _calculate_engagement_potential(self, audio_features: Dict[str, float]) -> float:
        """Calculate engagement potential based on audio features"""
        # Factors that drive engagement
        energy = audio_features.get('energy', 0.5)
        danceability = audio_features.get('danceability', 0.5)
        valence = audio_features.get('valence', 0.5)
        
        engagement_score = (energy * 0.4) + (danceability * 0.35) + (valence * 0.25)
        return engagement_score
    
    async def _calculate_playlist_potential(self, 
                                          metadata: SpotifyTrackMetadata,
                                          audio_features: Dict[str, float]) -> float:
        """Calculate playlist inclusion potential"""
        score = 0.5  # Base score
        
        # Popular genres get higher playlist potential
        genre_playlist_potential = {
            MusicGenre.POP: 0.9,
            MusicGenre.HIP_HOP: 0.85,
            MusicGenre.ELECTRONIC: 0.8,
            MusicGenre.R_AND_B: 0.75,
            MusicGenre.INDIE: 0.7
        }
        
        genre_score = genre_playlist_potential.get(metadata.genre, 0.6)
        
        # Audio features that work well in playlists
        if 0.4 <= audio_features.get('energy', 0.5) <= 0.8:
            score += 0.1
        if audio_features.get('danceability', 0.5) > 0.5:
            score += 0.1
        if audio_features.get('valence', 0.5) > 0.4:
            score += 0.1
        
        return (score + genre_score) / 2
    
    async def _generate_spotify_improvements(self, *scores) -> List[str]:
        """Generate improvement recommendations"""
        improvements = []
        
        metadata_score, discoverability_score, algorithmic_score, engagement_score, searchability_score, playlist_potential_score = scores
        
        if metadata_score < 0.7:
            improvements.append("Complete track metadata with genre, mood, and descriptive tags")
        
        if discoverability_score < 0.6:
            improvements.append("Optimize audio features for better algorithmic discovery")
        
        if searchability_score < 0.6:
            improvements.append("Add more relevant tags and improve track description")
        
        if playlist_potential_score < 0.6:
            improvements.append("Adjust audio characteristics to increase playlist inclusion chances")
        
        return improvements
    
    async def _identify_growth_opportunities(self, 
                                           metadata: SpotifyTrackMetadata,
                                           audio_features: Dict[str, float]) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        # Genre-specific opportunities
        if metadata.genre in [MusicGenre.ELECTRONIC, MusicGenre.HIP_HOP]:
            opportunities.append("Target gaming and fitness playlists")
        
        if audio_features.get('energy', 0.5) > 0.7:
            opportunities.append("Submit to high-energy workout playlists")
        
        if audio_features.get('valence', 0.5) > 0.7:
            opportunities.append("Target mood-boosting and positive vibes playlists")
        
        opportunities.append("Consider TikTok-friendly remix or shortened version")
        opportunities.append("Create acoustic or alternative versions for different audiences")
        
        return opportunities
    
    # Mock helper methods for playlist optimization
    async def _analyze_playlist_content(self, tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze playlist content"""
        return {'track_count': len(tracks), 'avg_energy': 0.6, 'dominant_genre': 'pop'}
    
    async def _optimize_playlist_title(self, title: str, analysis: Dict[str, Any]) -> str:
        """Optimize playlist title"""
        return title or "Curated Playlist"
    
    async def _optimize_playlist_description(self, analysis: Dict[str, Any]) -> str:
        """Optimize playlist description"""
        return "A carefully curated collection of tracks for every mood"
    
    async def _suggest_cover_art(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest cover art concepts"""
        return ["Vibrant gradient", "Minimalist text", "Genre-themed imagery"]
    
    async def _optimize_track_order(self, tracks: List[Dict[str, Any]]) -> List[str]:
        """Optimize track order"""
        return [f"track_{i}" for i in range(len(tracks))]
    
    async def _analyze_genre_flow(self, tracks: List[Dict[str, Any]]) -> List[MusicGenre]:
        """Analyze genre flow"""
        return [MusicGenre.POP] * len(tracks)
    
    async def _analyze_mood_progression(self, tracks: List[Dict[str, Any]]) -> List[str]:
        """Analyze mood progression"""
        return ["happy"] * len(tracks)
    
    async def _calculate_energy_curve(self, tracks: List[Dict[str, Any]]) -> List[float]:
        """Calculate energy curve"""
        return [0.6] * len(tracks)
    
    async def _calculate_optimal_duration(self, analysis: Dict[str, Any]) -> int:
        """Calculate optimal playlist duration"""
        return 60  # 60 minutes
    
    async def _predict_followers(self, analysis: Dict[str, Any]) -> int:
        """Predict follower potential"""
        return 1000  # Mock prediction
    
    async def _calculate_playlist_viral_potential(self, analysis: Dict[str, Any]) -> float:
        """Calculate playlist viral potential"""
        return 0.7  # Mock calculation