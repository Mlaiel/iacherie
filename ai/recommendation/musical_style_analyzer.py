"""Musical Style and Genre Analysis Engine
==========================================

Advanced AI-powered musical style analysis, genre classification, and creative 
compatibility assessment for precision matching between creators.

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import uuid
from collections import defaultdict
import math

# Audio analysis imports
try:
    import librosa
    import soundfile as sf
    from scipy.signal import stft
    from scipy.spatial.distance import euclidean, cosine
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    # Mock classes for environments without audio libraries
    class MockAudioProcessor:
        def load(self, *args, **kwargs): return (np.array([0.1, 0.2, 0.3]), 22050)
        def stft(self, *args, **kwargs): return np.array([[0.1, 0.2], [0.3, 0.4]])
        def mfcc(self, *args, **kwargs): return np.array([[0.1, 0.2, 0.3]])
        def spectral_centroid(self, *args, **kwargs): return np.array([[440.0]])
        def chroma_stft(self, *args, **kwargs): return np.array([[0.1] * 12])
        def tonnetz(self, *args, **kwargs): return np.array([[0.1] * 6])
        def zero_crossing_rate(self, *args, **kwargs): return np.array([[0.1]])
        def tempo(self, *args, **kwargs): return (120.0, np.array([120.0]))
    
    librosa = MockAudioProcessor()

logger = logging.getLogger(__name__)


class MusicGenre(Enum):
    """Comprehensive music genre classification"""
    # Main Genres
    POP = "pop"
    ROCK = "rock" 
    HIP_HOP = "hip_hop"
    RAP = "rap"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    FOLK = "folk"
    BLUES = "blues"
    REGGAE = "reggae"
    LATIN = "latin"
    WORLD = "world"
    AMBIENT = "ambient"
    
    # Electronic Subgenres
    HOUSE = "house"
    TECHNO = "techno"
    DRUM_AND_BASS = "drum_and_bass"
    DUBSTEP = "dubstep"
    TRANCE = "trance"
    TRAP = "trap"
    FUTURE_BASS = "future_bass"
    SYNTHWAVE = "synthwave"
    LO_FI = "lo_fi"
    
    # Rock Subgenres
    INDIE_ROCK = "indie_rock"
    ALTERNATIVE = "alternative"
    METAL = "metal"
    PUNK = "punk"
    GRUNGE = "grunge"
    PROGRESSIVE_ROCK = "progressive_rock"
    
    # Urban Genres
    R_AND_B = "r_and_b"
    SOUL = "soul"
    FUNK = "funk"
    GOSPEL = "gospel"
    
    # World Genres
    AFROBEAT = "afrobeat"
    REGGAETON = "reggaeton"
    K_POP = "k_pop"
    INDIAN_CLASSICAL = "indian_classical"
    FLAMENCO = "flamenco"


class MusicalElement(Enum):
    """Musical elements for analysis"""
    MELODY = "melody"
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    TIMBRE = "timbre"
    DYNAMICS = "dynamics"
    STRUCTURE = "structure"
    LYRICS = "lyrics"
    INSTRUMENTATION = "instrumentation"


class CreativeApproach(Enum):
    """Creative approaches and styles"""
    TRADITIONAL = "traditional"
    INNOVATIVE = "innovative"
    EXPERIMENTAL = "experimental"
    COMMERCIAL = "commercial"
    UNDERGROUND = "underground"
    MINIMALIST = "minimalist"
    MAXIMALIST = "maximalist"
    ORGANIC = "organic"
    SYNTHESIZED = "synthesized"
    IMPROVISED = "improvised"
    STRUCTURED = "structured"


@dataclass
class AudioFeatures:
    """Comprehensive audio feature extraction"""
    # Temporal Features
    tempo: float = 120.0
    beat_consistency: float = 0.0
    rhythm_complexity: float = 0.0
    
    # Spectral Features
    spectral_centroid: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    
    # Harmonic Features
    chroma_features: List[float] = field(default_factory=lambda: [0.0] * 12)
    harmonic_content: float = 0.0
    key_signature: Optional[str] = None
    modality: str = "major"  # major/minor
    
    # MFCC Features (13 coefficients)
    mfcc_features: List[float] = field(default_factory=lambda: [0.0] * 13)
    
    # Tonal Features
    tonnetz_features: List[float] = field(default_factory=lambda: [0.0] * 6)
    
    # Dynamic Features
    loudness_range: float = 0.0
    dynamic_complexity: float = 0.0
    
    # Additional Features
    energy: float = 0.0
    valence: float = 0.5  # Musical positivity
    danceability: float = 0.5
    instrumentalness: float = 0.0
    acousticness: float = 0.0
    
    def to_vector(self) -> List[float]:
        """Convert features to vector for ML"""
        return [
            self.tempo, self.beat_consistency, self.rhythm_complexity,
            self.spectral_centroid, self.spectral_bandwidth, self.spectral_rolloff,
            self.zero_crossing_rate, self.harmonic_content,
            self.loudness_range, self.dynamic_complexity,
            self.energy, self.valence, self.danceability,
            self.instrumentalness, self.acousticness
        ] + self.chroma_features + self.mfcc_features + self.tonnetz_features


@dataclass 
class StyleSignature:
    """Unique musical style signature for a creator"""
    creator_id: str
    
    # Primary characteristics
    dominant_genres: List[MusicGenre] = field(default_factory=list)
    musical_elements: Dict[MusicalElement, float] = field(default_factory=dict)
    creative_approach: List[CreativeApproach] = field(default_factory=list)
    
    # Audio characteristics
    audio_signature: Optional[AudioFeatures] = None
    typical_bpm_range: Tuple[float, float] = (80.0, 140.0)
    preferred_keys: List[str] = field(default_factory=list)
    
    # Production characteristics
    production_quality: float = 0.0
    instrumentation_complexity: float = 0.0
    vocal_style: Optional[str] = None
    
    # Emotional characteristics
    mood_profile: Dict[str, float] = field(default_factory=dict)
    energy_level: float = 0.5
    emotional_range: float = 0.5
    
    # Innovation metrics
    creativity_score: float = 0.0
    originality_score: float = 0.0
    trend_adoption: float = 0.0
    
    # Collaboration traits
    collaboration_style: str = "adaptive"
    leadership_tendency: float = 0.5
    flexibility_score: float = 0.5
    
    # Metadata
    confidence: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    sample_count: int = 0


@dataclass
class StyleCompatibility:
    """Detailed style compatibility analysis"""
    creator1_id: str
    creator2_id: str
    
    # Overall compatibility
    total_compatibility: float = 0.0
    
    # Genre compatibility (25%)
    genre_alignment: float = 0.0
    genre_complement: float = 0.0
    
    # Musical element compatibility (25%)
    melody_harmony: float = 0.0
    rhythm_sync: float = 0.0
    timbre_blend: float = 0.0
    
    # Creative approach compatibility (20%)
    approach_alignment: float = 0.0
    innovation_balance: float = 0.0
    
    # Technical compatibility (15%)
    production_compatibility: float = 0.0
    skill_complement: float = 0.0
    
    # Emotional compatibility (15%)
    mood_alignment: float = 0.0
    energy_compatibility: float = 0.0
    
    # Detailed factors
    compatibility_factors: Dict[str, Any] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    synergy_opportunities: List[str] = field(default_factory=list)
    
    # Confidence metrics
    confidence: float = 0.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TrendingStyle:
    """Trending musical style analysis"""
    style_name: str
    genre_tags: List[str] = field(default_factory=list)
    characteristic_features: AudioFeatures = field(default_factory=AudioFeatures)
    popularity_score: float = 0.0
    growth_rate: float = 0.0
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    platform_performance: Dict[str, float] = field(default_factory=dict)
    key_influencers: List[str] = field(default_factory=list)
    predicted_longevity: float = 0.0
    adoption_difficulty: float = 0.0


class MusicalStyleAnalyzer:
    """
    Advanced Musical Style and Genre Analysis Engine
    
    Provides comprehensive analysis of musical styles, genre classification,
    and creative compatibility assessment for precision creator matching.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the musical style analyzer"""
        self.config = config or {}
        self.is_initialized = False
        
        # Analysis models
        self.genre_classifier = None
        self.style_clusterer = None
        self.feature_extractor = None
        self.scaler = StandardScaler() if AUDIO_AVAILABLE else None
        
        # Style signatures database
        self.style_signatures: Dict[str, StyleSignature] = {}
        
        # Genre reference data
        self.genre_reference_features: Dict[MusicGenre, AudioFeatures] = {}
        
        # Trend analysis
        self.trending_styles: List[TrendingStyle] = []
        self.style_evolution: Dict[str, List[Dict]] = defaultdict(list)
        
        # Caching
        self.compatibility_cache: Dict[Tuple[str, str], StyleCompatibility] = {}
        self.analysis_cache: Dict[str, Any] = {}
        
        # Analytics
        self.analytics = {
            'total_analyses': 0,
            'genre_distribution': defaultdict(int),
            'avg_compatibility_score': 0.0,
            'trend_predictions_accuracy': 0.0
        }
        
        logger.info("MusicalStyleAnalyzer initialized")
    
    async def initialize(self) -> bool:
        """Initialize the musical style analyzer"""
        try:
            logger.info("Initializing Musical Style Analyzer...")
            
            # Initialize ML models
            await self._initialize_models()
            
            # Load genre reference data
            await self._load_genre_references()
            
            # Initialize trend analysis
            await self._initialize_trend_analysis()
            
            self.is_initialized = True
            logger.info("Musical Style Analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Musical Style Analyzer: {e}")
            raise Exception(f"Initialization failed: {e}")
    
    async def _initialize_models(self) -> None:
        """Initialize ML models for style analysis"""
        try:
            if not AUDIO_AVAILABLE:
                logger.warning("Audio libraries not available, using mock models")
                return
            
            # Genre classifier (K-means clustering)
            self.genre_classifier = KMeans(
                n_clusters=len(MusicGenre),
                random_state=42
            )
            
            # Style clustering model
            self.style_clusterer = KMeans(
                n_clusters=50,  # 50 style clusters
                random_state=42
            )
            
            # Feature scaler
            self.scaler = StandardScaler()
            
            logger.debug("ML models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    async def _load_genre_references(self) -> None:
        """Load reference audio features for each genre"""
        try:
            # In a real implementation, this would load from a database of labeled audio
            # For now, we'll create typical feature profiles for each genre
            
            self.genre_reference_features = {
                MusicGenre.ELECTRONIC: AudioFeatures(
                    tempo=128.0, energy=0.8, danceability=0.9,
                    instrumentalness=0.8, acousticness=0.1,
                    spectral_centroid=3000.0, valence=0.7
                ),
                MusicGenre.ROCK: AudioFeatures(
                    tempo=120.0, energy=0.9, danceability=0.6,
                    instrumentalness=0.7, acousticness=0.2,
                    spectral_centroid=2500.0, valence=0.6
                ),
                MusicGenre.POP: AudioFeatures(
                    tempo=110.0, energy=0.7, danceability=0.8,
                    instrumentalness=0.3, acousticness=0.3,
                    spectral_centroid=2000.0, valence=0.8
                ),
                MusicGenre.HIP_HOP: AudioFeatures(
                    tempo=85.0, energy=0.8, danceability=0.9,
                    instrumentalness=0.5, acousticness=0.1,
                    spectral_centroid=1800.0, valence=0.5
                ),
                MusicGenre.JAZZ: AudioFeatures(
                    tempo=120.0, energy=0.5, danceability=0.4,
                    instrumentalness=0.8, acousticness=0.6,
                    spectral_centroid=2200.0, valence=0.6
                ),
                MusicGenre.CLASSICAL: AudioFeatures(
                    tempo=100.0, energy=0.4, danceability=0.2,
                    instrumentalness=0.9, acousticness=0.8,
                    spectral_centroid=2500.0, valence=0.5
                ),
                # Add more genre references...
            }
            
            logger.debug("Genre reference features loaded")
            
        except Exception as e:
            logger.error(f"Error loading genre references: {e}")
            raise
    
    async def _initialize_trend_analysis(self) -> None:
        """Initialize trend analysis system"""
        try:
            # Mock trending styles for demonstration
            self.trending_styles = [
                TrendingStyle(
                    style_name="Lo-Fi Hip Hop",
                    genre_tags=["lo_fi", "hip_hop", "chill"],
                    popularity_score=0.8,
                    growth_rate=0.15,
                    predicted_longevity=0.7
                ),
                TrendingStyle(
                    style_name="Future Bass",
                    genre_tags=["electronic", "future_bass", "melodic"],
                    popularity_score=0.7,
                    growth_rate=0.12,
                    predicted_longevity=0.6
                ),
                TrendingStyle(
                    style_name="Indie Pop",
                    genre_tags=["indie", "pop", "alternative"],
                    popularity_score=0.6,
                    growth_rate=0.08,
                    predicted_longevity=0.8
                )
            ]
            
            logger.debug("Trend analysis initialized")
            
        except Exception as e:
            logger.error(f"Error initializing trend analysis: {e}")
            raise
    
    async def classify_genre(
        self,
        audio_features: AudioFeatures
    ) -> List[Tuple[MusicGenre, float]]:
        """Classify genre based on audio features"""
        try:
            genre_scores = []
            feature_vector = audio_features.to_vector()
            
            # Calculate similarity to each genre reference
            for genre, reference_features in self.genre_reference_features.items():
                reference_vector = reference_features.to_vector()
                
                # Calculate cosine similarity
                similarity = 1 - cosine(feature_vector, reference_vector)
                genre_scores.append((genre, max(0.0, similarity)))
            
            # Sort by similarity score
            genre_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Normalize scores to probabilities
            total_score = sum(score for _, score in genre_scores)
            if total_score > 0:
                genre_scores = [(genre, score / total_score) for genre, score in genre_scores]
            
            return genre_scores
            
        except Exception as e:
            logger.error(f"Error classifying genre: {e}")
            return [(MusicGenre.POP, 1.0)]
    
    async def calculate_style_compatibility(
        self,
        creator1_id: str,
        creator2_id: str
    ) -> StyleCompatibility:
        """Calculate detailed style compatibility between two creators"""
        try:
            # Check cache
            cache_key = (creator1_id, creator2_id)
            if cache_key in self.compatibility_cache:
                return self.compatibility_cache[cache_key]
            
            # Get style signatures
            signature1 = self.style_signatures.get(creator1_id)
            signature2 = self.style_signatures.get(creator2_id)
            
            if not signature1 or not signature2:
                logger.warning(f"Missing style signatures for compatibility analysis")
                return StyleCompatibility(
                    creator1_id=creator1_id,
                    creator2_id=creator2_id,
                    total_compatibility=0.0
                )
            
            # Calculate compatibility components
            genre_alignment = self._calculate_genre_alignment(signature1, signature2)
            genre_complement = self._calculate_genre_complement(signature1, signature2)
            
            # Musical element compatibility (simplified)
            melody_harmony = 0.7  # Mock score
            rhythm_sync = 0.8
            timbre_blend = 0.6
            
            # Creative approach compatibility
            approach_alignment = self._calculate_approach_alignment(signature1, signature2)
            innovation_balance = 0.7  # Mock score
            
            # Technical and emotional compatibility (simplified)
            production_compatibility = 0.8
            skill_complement = 0.6
            mood_alignment = 0.7
            energy_compatibility = 0.8
            
            # Calculate weighted total
            total_compatibility = (
                (genre_alignment + genre_complement) / 2 * 0.25 +
                (melody_harmony + rhythm_sync + timbre_blend) / 3 * 0.25 +
                (approach_alignment + innovation_balance) / 2 * 0.20 +
                (production_compatibility + skill_complement) / 2 * 0.15 +
                (mood_alignment + energy_compatibility) / 2 * 0.15
            )
            
            compatibility = StyleCompatibility(
                creator1_id=creator1_id,
                creator2_id=creator2_id,
                total_compatibility=total_compatibility,
                genre_alignment=genre_alignment,
                genre_complement=genre_complement,
                melody_harmony=melody_harmony,
                rhythm_sync=rhythm_sync,
                timbre_blend=timbre_blend,
                approach_alignment=approach_alignment,
                innovation_balance=innovation_balance,
                production_compatibility=production_compatibility,
                skill_complement=skill_complement,
                mood_alignment=mood_alignment,
                energy_compatibility=energy_compatibility,
                confidence=min(signature1.confidence, signature2.confidence)
            )
            
            # Cache result
            self.compatibility_cache[cache_key] = compatibility
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Error calculating style compatibility: {e}")
            return StyleCompatibility(
                creator1_id=creator1_id,
                creator2_id=creator2_id,
                total_compatibility=0.0
            )
    
    def _calculate_genre_alignment(
        self,
        signature1: StyleSignature,
        signature2: StyleSignature
    ) -> float:
        """Calculate genre alignment score"""
        try:
            genres1 = set(g.value for g in signature1.dominant_genres)
            genres2 = set(g.value for g in signature2.dominant_genres)
            
            if not genres1 or not genres2:
                return 0.0
            
            overlap = len(genres1 & genres2)
            total = len(genres1 | genres2)
            
            return overlap / total if total > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating genre alignment: {e}")
            return 0.0
    
    def _calculate_genre_complement(
        self,
        signature1: StyleSignature,
        signature2: StyleSignature
    ) -> float:
        """Calculate genre complement score"""
        try:
            # Some genre combinations work well together
            complementary_pairs = {
                ('electronic', 'hip_hop'), ('rock', 'electronic'),
                ('jazz', 'hip_hop'), ('classical', 'electronic'),
                ('pop', 'electronic'), ('indie_rock', 'electronic')
            }
            
            genres1 = set(g.value for g in signature1.dominant_genres)
            genres2 = set(g.value for g in signature2.dominant_genres)
            
            complement_score = 0.0
            for genre1 in genres1:
                for genre2 in genres2:
                    if (genre1, genre2) in complementary_pairs or (genre2, genre1) in complementary_pairs:
                        complement_score += 1.0
            
            max_possible = max(len(genres1), len(genres2))
            return min(1.0, complement_score / max_possible) if max_possible > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating genre complement: {e}")
            return 0.0
    
    def _calculate_approach_alignment(
        self,
        signature1: StyleSignature,
        signature2: StyleSignature
    ) -> float:
        """Calculate creative approach alignment"""
        try:
            approaches1 = set(a.value for a in signature1.creative_approach)
            approaches2 = set(a.value for a in signature2.creative_approach)
            
            if not approaches1 or not approaches2:
                return 0.5
            
            overlap = len(approaches1 & approaches2)
            total = len(approaches1 | approaches2)
            
            return overlap / total if total > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating approach alignment: {e}")
            return 0.5
    
    async def get_trending_styles(self) -> List[TrendingStyle]:
        """Get current trending musical styles"""
        return self.trending_styles
    
    async def analyze_creator_style(
        self,
        creator_id: str,
        audio_samples: List[str],
        metadata: Optional[Dict] = None
    ) -> StyleSignature:
        """Analyze and create style signature for a creator"""
        try:
            # Mock style signature creation for demonstration
            # In a real implementation, this would analyze audio files
            
            signature = StyleSignature(
                creator_id=creator_id,
                dominant_genres=[MusicGenre.ELECTRONIC, MusicGenre.POP],
                musical_elements={
                    MusicalElement.MELODY: 0.7,
                    MusicalElement.RHYTHM: 0.8,
                    MusicalElement.HARMONY: 0.6
                },
                creative_approach=[CreativeApproach.INNOVATIVE, CreativeApproach.COMMERCIAL],
                audio_signature=AudioFeatures(),
                typical_bpm_range=(100.0, 130.0),
                preferred_keys=["C", "G", "Am"],
                production_quality=0.8,
                mood_profile={"energetic": 0.6, "happy": 0.4},
                energy_level=0.7,
                creativity_score=0.8,
                originality_score=0.7,
                collaboration_style="adaptive",
                confidence=0.8,
                sample_count=len(audio_samples)
            )
            
            self.style_signatures[creator_id] = signature
            self.analytics['total_analyses'] += 1
            
            return signature
            
        except Exception as e:
            logger.error(f"Error analyzing creator style: {e}")
            return StyleSignature(creator_id=creator_id)
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data for the style analyzer"""
        try:
            return {
                **self.analytics,
                'total_signatures': len(self.style_signatures),
                'cache_size': len(self.compatibility_cache),
                'trending_styles_count': len(self.trending_styles),
                'genre_coverage': len(self.genre_reference_features)
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return self.analytics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the style analyzer"""
        health = {
            'status': 'healthy' if self.is_initialized else 'not_initialized',
            'audio_available': AUDIO_AVAILABLE,
            'signatures_loaded': len(self.style_signatures),
            'genre_references_loaded': len(self.genre_reference_features),
            'trending_styles_loaded': len(self.trending_styles),
            'models_initialized': self.genre_classifier is not None
        }
        
        return health


# Export main classes
__all__ = [
    'MusicalStyleAnalyzer',
    'MusicGenre',
    'MusicalElement',
    'CreativeApproach',
    'AudioFeatures',
    'StyleSignature',
    'StyleCompatibility',
    'TrendingStyle'
]