"""
Playlist Manager - Advanced Spotify Playlist Management & Recommendation Engine

Industrial-grade playlist management system with AI-powered curation, optimization algorithms,
and machine learning-based recommendation engine for enhanced music discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist, squareform
import networkx as nx

from .spotify_api import SpotifyAPIClient
from ...core.config import settings
from ...utils.caching import CacheManager
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class PlaylistOptimizationGoal(Enum):
    """Playlist optimization objectives"""
    FLOW = "flow"                    # Smooth musical transitions
    ENERGY = "energy"                # Energy level progression
    DISCOVERY = "discovery"          # Maximize new music discovery
    ENGAGEMENT = "engagement"        # Maximize listener retention
    DIVERSITY = "diversity"          # Musical variety and genre mixing
    DANCEABILITY = "danceability"    # Dance-focused progression
    MOOD = "mood"                    # Emotional journey optimization
    TEMPO = "tempo"                  # BPM-based progression

class PlaylistType(Enum):
    """Types of playlists for different optimization strategies"""
    WORKOUT = "workout"
    CHILL = "chill"
    PARTY = "party"
    FOCUS = "focus"
    SLEEP = "sleep"
    COMMUTE = "commute"
    DISCOVERY = "discovery"
    CUSTOM = "custom"

@dataclass
class TrackFeatures:
    """Comprehensive track feature analysis"""
    track_id: str
    audio_features: Dict[str, float] = field(default_factory=dict)
    popularity: int = 0
    explicit: bool = False
    duration_ms: int = 0
    key: int = 0
    mode: int = 0
    time_signature: int = 4
    genres: List[str] = field(default_factory=list)
    artists: List[str] = field(default_factory=list)
    release_date: Optional[datetime] = None
    
    # Computed features
    energy_level: str = "medium"
    mood_category: str = "neutral"
    complexity_score: float = 0.5
    commercial_appeal: float = 0.5

@dataclass
class PlaylistAnalysis:
    """Comprehensive playlist analysis results"""
    total_tracks: int = 0
    total_duration: float = 0.0  # in hours
    average_popularity: float = 0.0
    genre_distribution: Dict[str, float] = field(default_factory=dict)
    energy_profile: List[float] = field(default_factory=list)
    tempo_progression: List[float] = field(default_factory=list)
    mood_journey: List[str] = field(default_factory=list)
    artist_diversity: float = 0.0
    release_year_spread: Dict[str, int] = field(default_factory=dict)
    optimization_score: float = 0.0

class PlaylistManager:
    """Advanced playlist management with AI-powered optimization"""
    
    def __init__(self, api_client: SpotifyAPIClient):
        self.api_client = api_client
        self.cache_manager = CacheManager(prefix="playlist_manager")
        self.performance_monitor = PerformanceMonitor("playlist_manager")
        
        # ML components
        self.scaler = StandardScaler()
        self.track_clusterer = KMeans(n_clusters=8, random_state=42)
        self.similarity_threshold = 0.7
        
    async def create_playlist(self, name: str, description: str = "", 
                            public: bool = True, collaborative: bool = False,
                            access_token: str) -> Dict[str, Any]:
        """Create a new Spotify playlist"""
        try:
            # Get current user profile
            user_profile = await self.api_client.get_current_user_profile(access_token)
            user_id = user_profile["id"]
            
            # Create playlist
            playlist = await self.api_client.create_playlist(
                user_id=user_id,
                name=name,
                description=description,
                public=public,
                collaborative=collaborative,
                access_token=access_token
            )
            
            logger.info(f"Created playlist: {playlist['name']} (ID: {playlist['id']})")
            return playlist
            
        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            raise
    
    async def optimize_track_order(self, tracks: List[Dict[str, Any]], 
                                 goals: List[str]) -> List[Dict[str, Any]]:
        """Optimize track order using advanced algorithms"""
        if len(tracks) <= 1:
            return tracks
        
        try:
            # Extract audio features for all tracks
            track_features = await self._extract_track_features(tracks)
            
            # Apply optimization based on goals
            if PlaylistOptimizationGoal.FLOW.value in goals:
                optimized_tracks = await self._optimize_for_flow(track_features)
            elif PlaylistOptimizationGoal.ENERGY.value in goals:
                optimized_tracks = await self._optimize_for_energy_progression(track_features)
            elif PlaylistOptimizationGoal.DIVERSITY.value in goals:
                optimized_tracks = await self._optimize_for_diversity(track_features)
            elif PlaylistOptimizationGoal.DANCEABILITY.value in goals:
                optimized_tracks = await self._optimize_for_danceability(track_features)
            else:
                # Default optimization combines multiple factors
                optimized_tracks = await self._optimize_multi_objective(track_features, goals)
            
            return optimized_tracks
            
        except Exception as e:
            logger.error(f"Track order optimization failed: {e}")
            return tracks
    
    async def _extract_track_features(self, tracks: List[Dict[str, Any]]) -> List[TrackFeatures]:
        """Extract comprehensive features for tracks"""
        track_ids = [track["id"] for track in tracks]
        
        # Get audio features from Spotify
        audio_features = await self.api_client.get_audio_features(track_ids)
        
        track_features = []
        for i, track in enumerate(tracks):
            audio_feature = audio_features[i] if i < len(audio_features) and audio_features[i] else {}
            
            # Create TrackFeatures object
            features = TrackFeatures(
                track_id=track["id"],
                audio_features=audio_feature,
                popularity=track.get("popularity", 0),
                explicit=track.get("explicit", False),
                duration_ms=track.get("duration_ms", 0),
                artists=[artist["name"] for artist in track.get("artists", [])]
            )
            
            # Compute derived features
            if audio_feature:
                features.energy_level = self._categorize_energy_level(audio_feature.get("energy", 0.5))
                features.mood_category = self._determine_mood_category(audio_feature)
                features.complexity_score = self._calculate_complexity_score(audio_feature)
                features.commercial_appeal = self._assess_commercial_appeal(audio_feature, features.popularity)
            
            track_features.append(features)
        
        return track_features
    
    def _categorize_energy_level(self, energy: float) -> str:
        """Categorize energy level"""
        if energy >= 0.8:
            return "very_high"
        elif energy >= 0.6:
            return "high"
        elif energy >= 0.4:
            return "medium"
        elif energy >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _determine_mood_category(self, audio_features: Dict[str, float]) -> str:
        """Determine mood category based on audio features"""
        valence = audio_features.get("valence", 0.5)
        energy = audio_features.get("energy", 0.5)
        
        if valence > 0.6 and energy > 0.6:
            return "happy_energetic"
        elif valence > 0.6 and energy < 0.4:
            return "happy_calm"
        elif valence < 0.4 and energy > 0.6:
            return "aggressive_intense"
        elif valence < 0.4 and energy < 0.4:
            return "sad_melancholic"
        else:
            return "neutral_balanced"
    
    def _calculate_complexity_score(self, audio_features: Dict[str, float]) -> float:
        """Calculate musical complexity score"""
        # Combine multiple factors for complexity
        instrumentalness = audio_features.get("instrumentalness", 0)
        acousticness = audio_features.get("acousticness", 0)
        tempo = audio_features.get("tempo", 120)
        time_signature = audio_features.get("time_signature", 4)
        
        # Normalize tempo (typical range 60-200 BPM)
        normalized_tempo = min(1.0, max(0.0, (tempo - 60) / 140))
        
        # Calculate complexity (higher for more complex arrangements)
        complexity = (
            instrumentalness * 0.3 +
            (1 - acousticness) * 0.2 +  # Electronic/produced music tends to be more complex
            normalized_tempo * 0.2 +
            (time_signature / 7) * 0.3  # Unusual time signatures add complexity
        )
        
        return min(1.0, complexity)
    
    def _assess_commercial_appeal(self, audio_features: Dict[str, float], popularity: int) -> float:
        """Assess commercial appeal of a track"""
        # Factors that contribute to commercial appeal
        danceability = audio_features.get("danceability", 0.5)
        energy = audio_features.get("energy", 0.5)
        valence = audio_features.get("valence", 0.5)
        loudness = audio_features.get("loudness", -10)
        speechiness = audio_features.get("speechiness", 0.1)
        
        # Normalize loudness (typical range -60 to 0 dB)
        normalized_loudness = min(1.0, max(0.0, (loudness + 60) / 60))
        
        # Calculate appeal score
        appeal = (
            danceability * 0.25 +
            energy * 0.2 +
            valence * 0.15 +
            normalized_loudness * 0.15 +
            (popularity / 100) * 0.2 +
            (1 - speechiness) * 0.05  # Less speech = more musical
        )
        
        return min(1.0, appeal)
    
    async def _optimize_for_flow(self, track_features: List[TrackFeatures]) -> List[Dict[str, Any]]:
        """Optimize playlist for smooth musical flow"""
        if len(track_features) <= 2:
            return [self._get_original_track(tf) for tf in track_features]
        
        # Create feature matrix for similarity calculation
        feature_matrix = []
        for tf in track_features:
            af = tf.audio_features
            features = [
                af.get("danceability", 0.5),
                af.get("energy", 0.5),
                af.get("loudness", -10) / -60,  # Normalize loudness
                af.get("speechiness", 0.1),
                af.get("acousticness", 0.5),
                af.get("instrumentalness", 0.1),
                af.get("liveness", 0.1),
                af.get("valence", 0.5),
                af.get("tempo", 120) / 200,  # Normalize tempo
            ]
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(feature_matrix)
        
        # Use greedy algorithm to find smooth transitions
        optimized_order = self._find_optimal_path(similarity_matrix)
        
        return [self._get_original_track(track_features[i]) for i in optimized_order]
    
    def _find_optimal_path(self, similarity_matrix: np.ndarray) -> List[int]:
        """Find optimal path through tracks for smooth transitions"""
        n_tracks = len(similarity_matrix)
        if n_tracks <= 1:
            return list(range(n_tracks))
        
        # Start with the track that has highest average similarity
        avg_similarities = np.mean(similarity_matrix, axis=1)
        current_track = np.argmax(avg_similarities)
        
        path = [current_track]
        remaining_tracks = set(range(n_tracks)) - {current_track}
        
        # Greedy selection of next track based on similarity
        while remaining_tracks:
            similarities = similarity_matrix[current_track]
            
            # Find most similar remaining track
            best_similarity = -1
            best_track = None
            
            for track in remaining_tracks:
                if similarities[track] > best_similarity:
                    best_similarity = similarities[track]
                    best_track = track
            
            if best_track is not None:
                path.append(best_track)
                remaining_tracks.remove(best_track)
                current_track = best_track
            else:
                # Fallback: add any remaining track
                track = next(iter(remaining_tracks))
                path.append(track)
                remaining_tracks.remove(track)
                current_track = track
        
        return path
    
    async def _optimize_for_energy_progression(self, track_features: List[TrackFeatures]) -> List[Dict[str, Any]]:
        """Optimize playlist for energy level progression"""
        # Sort by energy level for smooth progression
        sorted_features = sorted(track_features, 
                               key=lambda tf: tf.audio_features.get("energy", 0.5))
        
        # Create energy curve (start medium, build up, then wind down)
        n_tracks = len(sorted_features)
        
        if n_tracks <= 3:
            return [self._get_original_track(tf) for tf in sorted_features]
        
        # Divide into sections: warm-up, peak, cool-down
        warm_up_size = n_tracks // 4
        peak_size = n_tracks // 2
        cool_down_size = n_tracks - warm_up_size - peak_size
        
        # Get tracks for each section
        low_energy = sorted_features[:warm_up_size + cool_down_size]
        high_energy = sorted_features[warm_up_size + cool_down_size:]
        
        # Arrange: medium -> high -> medium/low
        optimized_order = []
        
        # Warm-up: medium energy tracks
        optimized_order.extend(low_energy[:warm_up_size])
        
        # Peak: high energy tracks
        optimized_order.extend(high_energy)
        
        # Cool-down: remaining lower energy tracks
        optimized_order.extend(low_energy[warm_up_size:])
        
        return [self._get_original_track(tf) for tf in optimized_order]
    
    async def _optimize_for_diversity(self, track_features: List[TrackFeatures]) -> List[Dict[str, Any]]:
        """Optimize playlist for maximum musical diversity"""
        if len(track_features) <= 2:
            return [self._get_original_track(tf) for tf in track_features]
        
        # Create feature matrix
        feature_matrix = []
        for tf in track_features:
            af = tf.audio_features
            features = [
                af.get("danceability", 0.5),
                af.get("energy", 0.5),
                af.get("valence", 0.5),
                af.get("acousticness", 0.5),
                af.get("instrumentalness", 0.1),
                af.get("tempo", 120) / 200,
            ]
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        
        # Use clustering to identify diverse groups
        n_clusters = min(len(track_features) // 2, 5)
        if n_clusters < 2:
            return [self._get_original_track(tf) for tf in track_features]
        
        clusterer = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = clusterer.fit_predict(feature_matrix)
        
        # Interleave tracks from different clusters
        cluster_tracks = {i: [] for i in range(n_clusters)}
        for idx, cluster in enumerate(clusters):
            cluster_tracks[cluster].append(idx)
        
        # Create diverse ordering
        optimized_order = []
        max_cluster_size = max(len(tracks) for tracks in cluster_tracks.values())
        
        for i in range(max_cluster_size):
            for cluster_id in range(n_clusters):
                if i < len(cluster_tracks[cluster_id]):
                    optimized_order.append(cluster_tracks[cluster_id][i])
        
        return [self._get_original_track(track_features[i]) for i in optimized_order]
    
    async def _optimize_for_danceability(self, track_features: List[TrackFeatures]) -> List[Dict[str, Any]]:
        """Optimize playlist for danceability and tempo progression"""
        # Sort by danceability and tempo
        dance_scores = []
        for tf in track_features:
            af = tf.audio_features
            # Combine danceability and tempo appropriateness for dancing
            tempo = af.get("tempo", 120)
            danceability = af.get("danceability", 0.5)
            energy = af.get("energy", 0.5)
            
            # Optimal dance tempo range: 120-140 BPM
            tempo_score = 1.0 - abs(tempo - 130) / 70  # Peak at 130 BPM
            tempo_score = max(0, tempo_score)
            
            dance_score = danceability * 0.5 + energy * 0.3 + tempo_score * 0.2
            dance_scores.append((dance_score, tf))
        
        # Sort by dance score (descending)
        dance_scores.sort(key=lambda x: x[0], reverse=True)
        
        return [self._get_original_track(tf) for _, tf in dance_scores]
    
    async def _optimize_multi_objective(self, track_features: List[TrackFeatures], 
                                      goals: List[str]) -> List[Dict[str, Any]]:
        """Multi-objective optimization combining different goals"""
        if len(track_features) <= 2:
            return [self._get_original_track(tf) for tf in track_features]
        
        # Calculate scores for different objectives
        flow_scores = await self._calculate_flow_scores(track_features)
        energy_scores = self._calculate_energy_scores(track_features)
        diversity_scores = self._calculate_diversity_scores(track_features)
        
        # Weight different objectives based on goals
        weights = {
            PlaylistOptimizationGoal.FLOW.value: 0.3,
            PlaylistOptimizationGoal.ENERGY.value: 0.2,
            PlaylistOptimizationGoal.DIVERSITY.value: 0.2,
            PlaylistOptimizationGoal.ENGAGEMENT.value: 0.3
        }
        
        # Adjust weights based on specified goals
        for goal in goals:
            if goal in weights:
                weights[goal] = min(1.0, weights[goal] * 1.5)
        
        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}
        
        # Combine scores
        combined_scores = []
        for i, tf in enumerate(track_features):
            score = (
                flow_scores[i] * weights.get(PlaylistOptimizationGoal.FLOW.value, 0) +
                energy_scores[i] * weights.get(PlaylistOptimizationGoal.ENERGY.value, 0) +
                diversity_scores[i] * weights.get(PlaylistOptimizationGoal.DIVERSITY.value, 0) +
                (tf.popularity / 100) * weights.get(PlaylistOptimizationGoal.ENGAGEMENT.value, 0)
            )
            combined_scores.append((score, i, tf))
        
        # Sort by combined score
        combined_scores.sort(key=lambda x: x[0], reverse=True)
        
        return [self._get_original_track(tf) for _, _, tf in combined_scores]
    
    async def _calculate_flow_scores(self, track_features: List[TrackFeatures]) -> List[float]:
        """Calculate flow compatibility scores"""
        scores = []
        for tf in track_features:
            af = tf.audio_features
            # Flow score based on moderate values and consistency
            flow_score = 1.0 - abs(af.get("energy", 0.5) - 0.6)  # Prefer medium-high energy
            flow_score *= 1.0 - abs(af.get("valence", 0.5) - 0.6)  # Prefer positive mood
            scores.append(flow_score)
        return scores
    
    def _calculate_energy_scores(self, track_features: List[TrackFeatures]) -> List[float]:
        """Calculate energy progression scores"""
        return [tf.audio_features.get("energy", 0.5) for tf in track_features]
    
    def _calculate_diversity_scores(self, track_features: List[TrackFeatures]) -> List[float]:
        """Calculate diversity contribution scores"""
        # Simple diversity score based on feature variance
        scores = []
        for tf in track_features:
            af = tf.audio_features
            # Higher score for tracks that add diversity
            diversity_factors = [
                af.get("acousticness", 0.5),
                af.get("instrumentalness", 0.1),
                1.0 - af.get("speechiness", 0.1),  # Less speech = more diverse
                abs(af.get("tempo", 120) - 120) / 80  # Distance from average tempo
            ]
            scores.append(np.mean(diversity_factors))
        return scores
    
    def _get_original_track(self, track_feature: TrackFeatures) -> Dict[str, Any]:
        """Get original track data from TrackFeatures"""
        # In a real implementation, this would return the full track object
        # For now, return a simplified version
        return {
            "id": track_feature.track_id,
            "audio_features": track_feature.audio_features,
            "popularity": track_feature.popularity,
            "artists": track_feature.artists,
            "energy_level": track_feature.energy_level,
            "mood_category": track_feature.mood_category
        }
    
    async def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str],
                                   access_token: str) -> Dict[str, Any]:
        """Add tracks to existing playlist"""
        return await self.api_client.add_tracks_to_playlist(
            playlist_id, track_uris, access_token=access_token
        )
    
    async def analyze_playlist_composition(self, tracks: List[Dict[str, Any]]) -> PlaylistAnalysis:
        """Analyze playlist composition and provide insights"""
        if not tracks:
            return PlaylistAnalysis()
        
        track_features = await self._extract_track_features(tracks)
        
        # Calculate basic metrics
        total_tracks = len(tracks)
        total_duration = sum(track.get("duration_ms", 0) for track in tracks) / (1000 * 3600)  # hours
        avg_popularity = np.mean([track.get("popularity", 0) for track in tracks])
        
        # Genre distribution (simplified - would need genre analysis)
        artists = []
        for track in tracks:
            artists.extend([artist["name"] for artist in track.get("artists", [])])
        
        unique_artists = len(set(artists))
        artist_diversity = unique_artists / total_tracks if total_tracks > 0 else 0
        
        # Energy and mood profiles
        energy_profile = [tf.audio_features.get("energy", 0.5) for tf in track_features]
        tempo_progression = [tf.audio_features.get("tempo", 120) for tf in track_features]
        mood_journey = [tf.mood_category for tf in track_features]
        
        # Release year distribution (would need actual release dates)
        release_years = {}  # Placeholder
        
        return PlaylistAnalysis(
            total_tracks=total_tracks,
            total_duration=total_duration,
            average_popularity=avg_popularity,
            genre_distribution={},  # Would need genre analysis
            energy_profile=energy_profile,
            tempo_progression=tempo_progression,
            mood_journey=mood_journey,
            artist_diversity=artist_diversity,
            release_year_spread=release_years,
            optimization_score=np.mean(energy_profile)  # Simplified score
        )

class RecommendationEngine:
    """Advanced ML-powered recommendation engine"""
    
    def __init__(self):
        self.cache_manager = CacheManager(prefix="recommendation_engine")
        self.scaler = StandardScaler()
        
    async def enhance_recommendations(self, spotify_recommendations: List[Dict[str, Any]],
                                    seed_data: Dict[str, Any],
                                    user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance Spotify recommendations with ML-powered ranking"""
        if not spotify_recommendations:
            return []
        
        try:
            # Extract features for ranking
            features_matrix = []
            for track in spotify_recommendations:
                features = await self._extract_recommendation_features(track, seed_data, user_preferences)
                features_matrix.append(features)
            
            # Calculate recommendation scores
            scores = self._calculate_recommendation_scores(features_matrix, user_preferences)
            
            # Rank recommendations
            scored_recommendations = list(zip(spotify_recommendations, scores))
            scored_recommendations.sort(key=lambda x: x[1], reverse=True)
            
            return [track for track, score in scored_recommendations]
            
        except Exception as e:
            logger.error(f"Recommendation enhancement failed: {e}")
            return spotify_recommendations
    
    async def _extract_recommendation_features(self, track: Dict[str, Any],
                                             seed_data: Dict[str, Any],
                                             user_preferences: Dict[str, Any]) -> List[float]:
        """Extract features for recommendation scoring"""
        # Get audio features if available
        audio_features = track.get("audio_features", {})
        
        # Basic track features
        features = [
            track.get("popularity", 0) / 100,
            audio_features.get("danceability", 0.5),
            audio_features.get("energy", 0.5),
            audio_features.get("valence", 0.5),
            audio_features.get("acousticness", 0.5),
            audio_features.get("instrumentalness", 0.1),
            audio_features.get("liveness", 0.1),
            audio_features.get("speechiness", 0.1),
        ]
        
        # User preference alignment
        if user_preferences:
            pref_alignment = self._calculate_preference_alignment(audio_features, user_preferences)
            features.append(pref_alignment)
        else:
            features.append(0.5)
        
        # Seed similarity
        seed_similarity = self._calculate_seed_similarity(audio_features, seed_data)
        features.append(seed_similarity)
        
        return features
    
    def _calculate_preference_alignment(self, audio_features: Dict[str, float],
                                      user_preferences: Dict[str, Any]) -> float:
        """Calculate how well track aligns with user preferences"""
        if not user_preferences:
            return 0.5
        
        alignment_score = 0.5
        
        # Check preferred energy level
        preferred_energy = user_preferences.get("energy_level")
        if preferred_energy and "energy" in audio_features:
            energy = audio_features["energy"]
            if preferred_energy == "high" and energy > 0.7:
                alignment_score += 0.2
            elif preferred_energy == "medium" and 0.3 <= energy <= 0.7:
                alignment_score += 0.2
            elif preferred_energy == "low" and energy < 0.3:
                alignment_score += 0.2
        
        # Check mood preference
        preferred_mood = user_preferences.get("mood")
        if preferred_mood and "valence" in audio_features:
            valence = audio_features["valence"]
            if preferred_mood == "happy" and valence > 0.6:
                alignment_score += 0.2
            elif preferred_mood == "sad" and valence < 0.4:
                alignment_score += 0.2
            elif preferred_mood == "neutral" and 0.4 <= valence <= 0.6:
                alignment_score += 0.2
        
        return min(1.0, alignment_score)
    
    def _calculate_seed_similarity(self, audio_features: Dict[str, float],
                                 seed_data: Dict[str, Any]) -> float:
        """Calculate similarity to seed tracks/artists"""
        if not seed_data or not audio_features:
            return 0.5
        
        # Target audio features from seed data
        target_features = seed_data.get("target_audio_features", {})
        if not target_features:
            return 0.5
        
        # Calculate feature similarity
        similarities = []
        for feature in ["danceability", "energy", "valence", "acousticness"]:
            if feature in target_features and feature in audio_features:
                target_value = target_features[feature]
                track_value = audio_features[feature]
                similarity = 1.0 - abs(target_value - track_value)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    def _calculate_recommendation_scores(self, features_matrix: List[List[float]],
                                       user_preferences: Dict[str, Any]) -> List[float]:
        """Calculate recommendation scores using ML model"""
        if not features_matrix:
            return []
        
        # Simple scoring based on feature weights
        # In production, this would use a trained ML model
        feature_weights = [
            0.2,  # popularity
            0.15, # danceability
            0.15, # energy
            0.15, # valence
            0.1,  # acousticness
            0.05, # instrumentalness
            0.05, # liveness
            0.05, # speechiness
            0.05, # preference alignment
            0.05  # seed similarity
        ]
        
        scores = []
        for features in features_matrix:
            # Ensure features list has the right length
            if len(features) < len(feature_weights):
                features.extend([0.5] * (len(feature_weights) - len(features)))
            
            score = sum(f * w for f, w in zip(features, feature_weights))
            scores.append(score)
        
        return scores
