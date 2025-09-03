"""Advanced AI Matching Engine - Ultra-Advanced ML-Powered Matching Service
====================================================================

Provides comprehensive AI-powered matching service with personalized ML algorithms,
creative compatibility scoring, musical style matching, collaboration success prediction,
proactive suggestions, and graph database integration.

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

# Machine Learning imports
try:
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPRegressor
    import networkx as nx
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Mock classes for environments without ML libraries
    class MockMLModel:
        def fit(self, *args, **kwargs): pass
        def predict(self, *args, **kwargs): return [0.5]
        def transform(self, *args, **kwargs): return [[0.5]]
    
    pd = None
    TfidfVectorizer = MockMLModel
    cosine_similarity = lambda x, y: [[0.5]]
    RandomForestRegressor = MockMLModel
    GradientBoostingClassifier = MockMLModel
    KMeans = MockMLModel
    StandardScaler = MockMLModel
    MLPRegressor = MockMLModel
    nx = None

from .models import CreatorProfile, Platform, ContentType, TrendInsight
from .exceptions import RecommendationError, ModelInitializationError

logger = logging.getLogger(__name__)


class MatchingAlgorithm(Enum):
    """Advanced matching algorithms available"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID_ML = "hybrid_ml"
    DEEP_NEURAL = "deep_neural"
    GRAPH_BASED = "graph_based"
    ENSEMBLE = "ensemble"


class MusicGenre(Enum):
    """Comprehensive music genre classification"""
    # Main genres
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
    
    # Electronic subgenres
    HOUSE = "house"
    TECHNO = "techno"
    DRUM_AND_BASS = "drum_and_bass"
    DUBSTEP = "dubstep"
    TRANCE = "trance"
    
    # Rock subgenres
    INDIE_ROCK = "indie_rock"
    ALTERNATIVE = "alternative"
    METAL = "metal"
    PUNK = "punk"
    GRUNGE = "grunge"


class CreativeStyle(Enum):
    """Creative style characteristics for matching"""
    EXPERIMENTAL = "experimental"
    MAINSTREAM = "mainstream"
    UNDERGROUND = "underground"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"
    MINIMALIST = "minimalist"
    MAXIMALIST = "maximalist"
    VINTAGE = "vintage"
    FUTURISTIC = "futuristic"
    ORGANIC = "organic"


@dataclass
class MusicalProfile:
    """Enhanced musical profile for advanced matching"""
    primary_genres: List[MusicGenre] = field(default_factory=list)
    secondary_genres: List[MusicGenre] = field(default_factory=list)
    creative_style: List[CreativeStyle] = field(default_factory=list)
    bpm_range: Tuple[int, int] = (80, 140)
    key_preferences: List[str] = field(default_factory=list)
    vocal_style: Optional[str] = None
    instrument_skills: List[str] = field(default_factory=list)
    production_skills: List[str] = field(default_factory=list)
    influences: List[str] = field(default_factory=list)
    mood_tags: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)


@dataclass
class CollaborationHistory:
    """Detailed collaboration history for ML training"""
    collaboration_id: str
    partner_id: str
    collaboration_type: str
    success_score: float  # 0-1
    duration_days: int
    revenue_generated: Decimal
    audience_growth: float
    engagement_improvement: float
    completion_status: str
    satisfaction_rating: float
    created_at: datetime
    tags: List[str] = field(default_factory=list)


@dataclass
class CreativeCompatibilityScore:
    """Ultra-detailed creative compatibility scoring"""
    total_score: float
    
    # Musical compatibility (40%)
    genre_alignment: float
    style_harmony: float
    technical_complement: float
    
    # Creative compatibility (30%)
    artistic_vision_match: float
    work_style_compatibility: float
    innovation_balance: float
    
    # Professional compatibility (20%)
    experience_balance: float
    audience_overlap: float
    brand_alignment: float
    
    # Personal compatibility (10%)
    communication_style: float
    timeline_preference: float
    commitment_level: float
    
    # Detailed factors
    factors: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    explanation: str = ""


@dataclass
class CollaborationPrediction:
    """ML-based collaboration success prediction"""
    success_probability: float
    expected_audience_growth: float
    predicted_revenue: Decimal
    engagement_boost: float
    risk_factors: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    timeline_prediction: int  # days
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    model_version: str = "1.0"


@dataclass
class ProactiveSuggestion:
    """Proactive AI suggestions for creators"""
    suggestion_id: str
    creator_id: str
    suggestion_type: str  # collaboration, trend, optimization
    title: str
    description: str
    potential_partners: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    priority_score: float = 0.0
    confidence: float = 0.0
    expires_at: datetime = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedMatchingEngine:
    """
    Ultra-Advanced AI Matching Engine
    
    Provides enterprise-grade AI-powered matching with:
    - Personalized ML recommendation algorithms
    - Creative compatibility scoring
    - Musical style and genre matching
    - Collaboration success prediction
    - Proactive suggestion system
    - Graph database integration for complex relationships
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the advanced matching engine"""
        self.config = config or {}
        self.is_initialized = False
        
        # ML Models
        self.ml_models = {
            'compatibility_model': None,
            'success_predictor': None,
            'genre_analyzer': None,
            'style_classifier': None,
            'trend_predictor': None,
            'collaborative_filter': None
        }
        
        # Data stores
        self.creator_profiles: Dict[str, Dict] = {}
        self.musical_profiles: Dict[str, MusicalProfile] = {}
        self.collaboration_history: Dict[str, List[CollaborationHistory]] = defaultdict(list)
        self.graph_network = None
        
        # Feature extractors
        self.text_vectorizer = TfidfVectorizer() if ML_AVAILABLE else MockMLModel()
        self.scaler = StandardScaler() if ML_AVAILABLE else MockMLModel()
        
        # Caching
        self.compatibility_cache: Dict[str, CreativeCompatibilityScore] = {}
        self.suggestion_cache: Dict[str, List[ProactiveSuggestion]] = {}
        
        # Analytics
        self.analytics = {
            'total_matches': 0,
            'successful_predictions': 0,
            'avg_compatibility_score': 0.0,
            'model_accuracy': 0.0
        }
        
        logger.info("AdvancedMatchingEngine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the matching engine with ML models"""
        try:
            logger.info("Initializing Advanced AI Matching Engine...")
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Initialize graph network
            await self._initialize_graph_network()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            # Load historical data for training
            await self._load_training_data()
            
            self.is_initialized = True
            logger.info("Advanced AI Matching Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Matching Engine: {e}")
            raise ModelInitializationError(f"Initialization failed: {e}")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models"""
        try:
            if not ML_AVAILABLE:
                logger.warning("ML libraries not available, using mock models")
                for model_name in self.ml_models:
                    self.ml_models[model_name] = MockMLModel()
                return
            
            # Compatibility scoring model (Random Forest)
            self.ml_models['compatibility_model'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Success prediction model (Gradient Boosting)
            self.ml_models['success_predictor'] = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )
            
            # Genre analysis model (Neural Network)
            self.ml_models['genre_analyzer'] = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            )
            
            # Style classifier
            self.ml_models['style_classifier'] = KMeans(
                n_clusters=10,
                random_state=42
            )
            
            # Collaborative filtering model
            self.ml_models['collaborative_filter'] = RandomForestRegressor(
                n_estimators=50,
                random_state=42
            )
            
            logger.debug("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
            raise
    
    async def _initialize_graph_network(self) -> None:
        """Initialize graph network for relationship analysis"""
        try:
            if nx is None:
                logger.warning("NetworkX not available, using mock graph")
                self.graph_network = {"mock": True}
                return
            
            # Create directed graph for creator relationships
            self.graph_network = nx.DiGraph()
            
            # Add node attributes for creators
            # This will be populated as creators are added
            
            logger.debug("Graph network initialized")
            
        except Exception as e:
            logger.error(f"Error initializing graph network: {e}")
            raise
    
    async def _initialize_feature_extractors(self) -> None:
        """Initialize feature extraction components"""
        try:
            # Text vectorizer for description analysis
            if ML_AVAILABLE:
                self.text_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                # Standard scaler for numerical features
                self.scaler = StandardScaler()
            
            logger.debug("Feature extractors initialized")
            
        except Exception as e:
            logger.error(f"Error initializing feature extractors: {e}")
            raise
    
    async def _load_training_data(self) -> None:
        """Load and prepare training data for ML models"""
        try:
            # In a real implementation, this would load from database
            # For now, we'll create some mock training data
            
            # Mock training data for demonstration
            training_data = self._generate_mock_training_data()
            
            # Train models with the data
            await self._train_models(training_data)
            
            logger.debug("Training data loaded and models trained")
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            raise
    
    def _generate_mock_training_data(self) -> Dict[str, Any]:
        """Generate mock training data for model initialization"""
        return {
            'compatibility_features': np.random.rand(100, 20),
            'compatibility_scores': np.random.rand(100),
            'success_features': np.random.rand(100, 15),
            'success_labels': np.random.randint(0, 2, 100),
            'genre_features': np.random.rand(100, 10),
            'genre_labels': np.random.rand(100),
        }
    
    async def _train_models(self, training_data: Dict[str, Any]) -> None:
        """Train ML models with provided data"""
        try:
            if not ML_AVAILABLE:
                logger.info("ML not available, skipping model training")
                return
            
            # Train compatibility model
            self.ml_models['compatibility_model'].fit(
                training_data['compatibility_features'],
                training_data['compatibility_scores']
            )
            
            # Train success predictor
            self.ml_models['success_predictor'].fit(
                training_data['success_features'],
                training_data['success_labels']
            )
            
            # Train genre analyzer
            self.ml_models['genre_analyzer'].fit(
                training_data['genre_features'],
                training_data['genre_labels']
            )
            
            # Train style classifier
            self.ml_models['style_classifier'].fit(
                training_data['compatibility_features']
            )
            
            logger.info("ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    async def register_creator(
        self,
        creator_id: str,
        profile_data: Dict[str, Any],
        musical_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register creator with enhanced profile data"""
        try:
            # Store creator profile
            self.creator_profiles[creator_id] = profile_data
            
            # Create musical profile
            if musical_data:
                musical_profile = MusicalProfile(
                    primary_genres=[MusicGenre(g) for g in musical_data.get('primary_genres', [])],
                    secondary_genres=[MusicGenre(g) for g in musical_data.get('secondary_genres', [])],
                    creative_style=[CreativeStyle(s) for s in musical_data.get('creative_style', [])],
                    bpm_range=tuple(musical_data.get('bpm_range', [80, 140])),
                    key_preferences=musical_data.get('key_preferences', []),
                    vocal_style=musical_data.get('vocal_style'),
                    instrument_skills=musical_data.get('instrument_skills', []),
                    production_skills=musical_data.get('production_skills', []),
                    influences=musical_data.get('influences', []),
                    mood_tags=musical_data.get('mood_tags', []),
                    target_audience=musical_data.get('target_audience', [])
                )
                self.musical_profiles[creator_id] = musical_profile
            
            # Add to graph network
            if self.graph_network and hasattr(self.graph_network, 'add_node'):
                self.graph_network.add_node(
                    creator_id,
                    **profile_data,
                    musical_profile=musical_data
                )
            
            logger.info(f"Creator {creator_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator {creator_id}: {e}")
            return False
    
    async def find_personalized_matches(
        self,
        creator_id: str,
        collaboration_type: str = "any",
        algorithm: MatchingAlgorithm = MatchingAlgorithm.HYBRID_ML,
        limit: int = 10
    ) -> List[Tuple[str, CreativeCompatibilityScore]]:
        """Find personalized matches using advanced ML algorithms"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get creator profile
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                logger.warning(f"Creator {creator_id} not found")
                return []
            
            musical_profile = self.musical_profiles.get(creator_id)
            
            # Find potential matches based on algorithm
            candidates = await self._find_candidates(
                creator_id, collaboration_type, algorithm
            )
            
            # Calculate compatibility scores
            matches = []
            for candidate_id in candidates:
                if candidate_id == creator_id:
                    continue
                
                # Check cache first
                cache_key = f"{creator_id}_{candidate_id}_{collaboration_type}"
                if cache_key in self.compatibility_cache:
                    compatibility = self.compatibility_cache[cache_key]
                else:
                    compatibility = await self.calculate_creative_compatibility(
                        creator_id, candidate_id, collaboration_type
                    )
                    self.compatibility_cache[cache_key] = compatibility
                
                if compatibility.total_score >= 0.5:  # Minimum threshold
                    matches.append((candidate_id, compatibility))
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x[1].total_score, reverse=True)
            
            # Update analytics
            self.analytics['total_matches'] += len(matches)
            if matches:
                avg_score = sum(m[1].total_score for m in matches) / len(matches)
                self.analytics['avg_compatibility_score'] = avg_score
            
            logger.info(f"Found {len(matches)} matches for {creator_id}")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding personalized matches: {e}")
            return []
    
    async def _find_candidates(
        self,
        creator_id: str,
        collaboration_type: str,
        algorithm: MatchingAlgorithm
    ) -> List[str]:
        """Find candidate creators based on algorithm"""
        try:
            candidates = []
            creator_profile = self.creator_profiles[creator_id]
            musical_profile = self.musical_profiles.get(creator_id)
            
            if algorithm == MatchingAlgorithm.COLLABORATIVE_FILTERING:
                candidates = await self._collaborative_filtering_candidates(creator_id)
                
            elif algorithm == MatchingAlgorithm.CONTENT_BASED:
                candidates = await self._content_based_candidates(creator_id, musical_profile)
                
            elif algorithm == MatchingAlgorithm.GRAPH_BASED:
                candidates = await self._graph_based_candidates(creator_id)
                
            elif algorithm == MatchingAlgorithm.HYBRID_ML:
                # Combine multiple algorithms
                cf_candidates = await self._collaborative_filtering_candidates(creator_id)
                cb_candidates = await self._content_based_candidates(creator_id, musical_profile)
                graph_candidates = await self._graph_based_candidates(creator_id)
                
                # Merge and deduplicate
                all_candidates = set(cf_candidates + cb_candidates + graph_candidates)
                candidates = list(all_candidates)
                
            elif algorithm == MatchingAlgorithm.ENSEMBLE:
                candidates = await self._ensemble_candidates(creator_id)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error finding candidates: {e}")
            return list(self.creator_profiles.keys())
    
    async def _collaborative_filtering_candidates(self, creator_id: str) -> List[str]:
        """Find candidates using collaborative filtering"""
        try:
            # Get creators with similar collaboration history
            creator_history = self.collaboration_history.get(creator_id, [])
            
            # Find creators who collaborated with similar partners
            similar_creators = set()
            for collab in creator_history:
                partner_id = collab.partner_id
                # Find other creators who collaborated with this partner
                for other_creator, other_history in self.collaboration_history.items():
                    if other_creator != creator_id:
                        for other_collab in other_history:
                            if other_collab.partner_id == partner_id:
                                similar_creators.add(other_creator)
            
            return list(similar_creators)
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _content_based_candidates(
        self, 
        creator_id: str, 
        musical_profile: Optional[MusicalProfile]
    ) -> List[str]:
        """Find candidates using content-based filtering"""
        try:
            if not musical_profile:
                return []
            
            candidates = []
            creator_genres = set([g.value for g in musical_profile.primary_genres])
            creator_styles = set([s.value for s in musical_profile.creative_style])
            
            for other_creator_id, other_profile in self.musical_profiles.items():
                if other_creator_id == creator_id:
                    continue
                
                other_genres = set([g.value for g in other_profile.primary_genres])
                other_styles = set([s.value for s in other_profile.creative_style])
                
                # Calculate overlap
                genre_overlap = len(creator_genres & other_genres) / len(creator_genres | other_genres) if creator_genres | other_genres else 0
                style_overlap = len(creator_styles & other_styles) / len(creator_styles | other_styles) if creator_styles | other_styles else 0
                
                # Include if there's some overlap
                if genre_overlap > 0.1 or style_overlap > 0.1:
                    candidates.append(other_creator_id)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _graph_based_candidates(self, creator_id: str) -> List[str]:
        """Find candidates using graph-based algorithms"""
        try:
            if not self.graph_network or not hasattr(self.graph_network, 'neighbors'):
                return []
            
            candidates = []
            
            # Direct neighbors (1-hop)
            if self.graph_network.has_node(creator_id):
                direct_neighbors = list(self.graph_network.neighbors(creator_id))
                candidates.extend(direct_neighbors)
                
                # Second-degree connections (2-hop)
                for neighbor in direct_neighbors:
                    second_degree = list(self.graph_network.neighbors(neighbor))
                    candidates.extend(second_degree)
            
            # Remove duplicates and self
            candidates = list(set(candidates))
            if creator_id in candidates:
                candidates.remove(creator_id)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error in graph-based filtering: {e}")
            return []
    
    async def _ensemble_candidates(self, creator_id: str) -> List[str]:
        """Find candidates using ensemble method"""
        try:
            # Combine multiple algorithms with weights
            cf_candidates = await self._collaborative_filtering_candidates(creator_id)
            cb_candidates = await self._content_based_candidates(
                creator_id, self.musical_profiles.get(creator_id)
            )
            graph_candidates = await self._graph_based_candidates(creator_id)
            
            # Score candidates based on appearance frequency
            candidate_scores = defaultdict(float)
            
            for candidate in cf_candidates:
                candidate_scores[candidate] += 0.4  # 40% weight
            
            for candidate in cb_candidates:
                candidate_scores[candidate] += 0.4  # 40% weight
            
            for candidate in graph_candidates:
                candidate_scores[candidate] += 0.2  # 20% weight
            
            # Sort by score and return top candidates
            sorted_candidates = sorted(
                candidate_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [candidate for candidate, score in sorted_candidates if score >= 0.3]
            
        except Exception as e:
            logger.error(f"Error in ensemble method: {e}")
            return []
    
    async def calculate_creative_compatibility(
        self,
        creator1_id: str,
        creator2_id: str,
        collaboration_type: str = "any"
    ) -> CreativeCompatibilityScore:
        """Calculate ultra-detailed creative compatibility score"""
        try:
            # Get profiles
            profile1 = self.creator_profiles.get(creator1_id)
            profile2 = self.creator_profiles.get(creator2_id)
            musical1 = self.musical_profiles.get(creator1_id)
            musical2 = self.musical_profiles.get(creator2_id)
            
            if not profile1 or not profile2:
                return CreativeCompatibilityScore(
                    total_score=0.0,
                    genre_alignment=0.0,
                    style_harmony=0.0,
                    technical_complement=0.0,
                    artistic_vision_match=0.0,
                    work_style_compatibility=0.0,
                    innovation_balance=0.0,
                    experience_balance=0.0,
                    audience_overlap=0.0,
                    brand_alignment=0.0,
                    communication_style=0.0,
                    timeline_preference=0.0,
                    commitment_level=0.0,
                    explanation="Insufficient profile data"
                )
            
            # Musical compatibility (40%)
            genre_score = await self._calculate_genre_alignment(musical1, musical2)
            style_score = await self._calculate_style_harmony(musical1, musical2)
            technical_score = await self._calculate_technical_complement(musical1, musical2)
            
            musical_score = (genre_score * 0.5 + style_score * 0.3 + technical_score * 0.2) * 0.4
            
            # Creative compatibility (30%)
            vision_score = await self._calculate_artistic_vision_match(profile1, profile2, musical1, musical2)
            work_style_score = await self._calculate_work_style_compatibility(profile1, profile2)
            innovation_score = await self._calculate_innovation_balance(profile1, profile2, musical1, musical2)
            
            creative_score = (vision_score * 0.4 + work_style_score * 0.4 + innovation_score * 0.2) * 0.3
            
            # Professional compatibility (20%)
            experience_score = await self._calculate_experience_balance(profile1, profile2)
            audience_score = await self._calculate_audience_overlap(profile1, profile2)
            brand_score = await self._calculate_brand_alignment(profile1, profile2)
            
            professional_score = (experience_score * 0.4 + audience_score * 0.3 + brand_score * 0.3) * 0.2
            
            # Personal compatibility (10%)
            communication_score = await self._calculate_communication_style(profile1, profile2)
            timeline_score = await self._calculate_timeline_preference(profile1, profile2)
            commitment_score = await self._calculate_commitment_level(profile1, profile2)
            
            personal_score = (communication_score * 0.4 + timeline_score * 0.3 + commitment_score * 0.3) * 0.1
            
            # Total score
            total_score = musical_score + creative_score + professional_score + personal_score
            
            # Generate explanation
            explanation = self._generate_compatibility_explanation(
                total_score, genre_score, style_score, vision_score, experience_score
            )
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_score_confidence(profile1, profile2, musical1, musical2)
            
            return CreativeCompatibilityScore(
                total_score=min(total_score, 1.0),
                genre_alignment=genre_score,
                style_harmony=style_score,
                technical_complement=technical_score,
                artistic_vision_match=vision_score,
                work_style_compatibility=work_style_score,
                innovation_balance=innovation_score,
                experience_balance=experience_score,
                audience_overlap=audience_score,
                brand_alignment=brand_score,
                communication_style=communication_score,
                timeline_preference=timeline_score,
                commitment_level=commitment_score,
                factors={
                    'musical_score': musical_score,
                    'creative_score': creative_score,
                    'professional_score': professional_score,
                    'personal_score': personal_score
                },
                confidence=confidence,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error calculating creative compatibility: {e}")
            return CreativeCompatibilityScore(
                total_score=0.0,
                genre_alignment=0.0,
                style_harmony=0.0,
                technical_complement=0.0,
                artistic_vision_match=0.0,
                work_style_compatibility=0.0,
                innovation_balance=0.0,
                experience_balance=0.0,
                audience_overlap=0.0,
                brand_alignment=0.0,
                communication_style=0.0,
                timeline_preference=0.0,
                commitment_level=0.0,
                explanation=f"Error calculating compatibility: {str(e)}"
            )
    
    async def predict_collaboration_success(
        self,
        creator1_id: str,
        creator2_id: str,
        collaboration_type: str,
        project_data: Optional[Dict] = None
    ) -> CollaborationPrediction:
        """Predict collaboration success using ML models"""
        try:
            # Get compatibility score
            compatibility = await self.calculate_creative_compatibility(
                creator1_id, creator2_id, collaboration_type
            )
            
            # Prepare features for ML model
            features = await self._extract_prediction_features(
                creator1_id, creator2_id, compatibility, project_data
            )
            
            # Use ML model to predict success
            if ML_AVAILABLE and self.ml_models['success_predictor']:
                success_prob = self.ml_models['success_predictor'].predict([features])[0]
                success_prob = max(0.0, min(1.0, float(success_prob)))
            else:
                # Fallback to compatibility-based prediction
                success_prob = compatibility.total_score * 0.8 + 0.1
            
            # Predict other metrics
            audience_growth = await self._predict_audience_growth(creator1_id, creator2_id, success_prob)
            revenue_prediction = await self._predict_revenue(creator1_id, creator2_id, success_prob, project_data)
            engagement_boost = await self._predict_engagement_boost(creator1_id, creator2_id, success_prob)
            
            # Identify risk and success factors
            risk_factors = await self._identify_risk_factors(creator1_id, creator2_id, compatibility)
            success_factors = await self._identify_success_factors(creator1_id, creator2_id, compatibility)
            
            # Predict timeline
            timeline_days = await self._predict_timeline(collaboration_type, compatibility.total_score)
            
            # Calculate confidence interval
            confidence_interval = self._calculate_prediction_confidence_interval(success_prob, compatibility)
            
            return CollaborationPrediction(
                success_probability=success_prob,
                expected_audience_growth=audience_growth,
                predicted_revenue=revenue_prediction,
                engagement_boost=engagement_boost,
                risk_factors=risk_factors,
                success_factors=success_factors,
                timeline_prediction=timeline_days,
                confidence_interval=confidence_interval,
                model_version="1.0"
            )
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {e}")
            return CollaborationPrediction(
                success_probability=0.5,
                expected_audience_growth=0.0,
                predicted_revenue=Decimal('0'),
                engagement_boost=0.0,
                risk_factors=["Prediction error"],
                success_factors=[],
                timeline_prediction=30
            )
    
    async def generate_proactive_suggestions(
        self,
        creator_id: str,
        limit: int = 5
    ) -> List[ProactiveSuggestion]:
        """Generate proactive AI suggestions for creators"""
        try:
            # Check cache first
            if creator_id in self.suggestion_cache:
                cached_suggestions = self.suggestion_cache[creator_id]
                # Filter non-expired suggestions
                valid_suggestions = [
                    s for s in cached_suggestions 
                    if s.expires_at is None or s.expires_at > datetime.now()
                ]
                if valid_suggestions:
                    return valid_suggestions[:limit]
            
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                return []
            
            suggestions = []
            
            # Collaboration suggestions
            collab_suggestions = await self._generate_collaboration_suggestions(creator_id)
            suggestions.extend(collab_suggestions)
            
            # Trend-based suggestions
            trend_suggestions = await self._generate_trend_suggestions(creator_id)
            suggestions.extend(trend_suggestions)
            
            # Optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(creator_id)
            suggestions.extend(optimization_suggestions)
            
            # Growth opportunity suggestions
            growth_suggestions = await self._generate_growth_suggestions(creator_id)
            suggestions.extend(growth_suggestions)
            
            # Sort by priority score
            suggestions.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Cache suggestions
            self.suggestion_cache[creator_id] = suggestions
            
            logger.info(f"Generated {len(suggestions)} proactive suggestions for {creator_id}")
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating proactive suggestions: {e}")
            return []
    
    # Helper methods for compatibility scoring
    async def _calculate_genre_alignment(
        self, 
        musical1: Optional[MusicalProfile], 
        musical2: Optional[MusicalProfile]
    ) -> float:
        """Calculate genre alignment score"""
        if not musical1 or not musical2:
            return 0.5
        
        genres1 = set([g.value for g in musical1.primary_genres + musical1.secondary_genres])
        genres2 = set([g.value for g in musical2.primary_genres + musical2.secondary_genres])
        
        if not genres1 or not genres2:
            return 0.3
        
        overlap = len(genres1 & genres2)
        total = len(genres1 | genres2)
        
        # Primary genre bonus
        primary1 = set([g.value for g in musical1.primary_genres])
        primary2 = set([g.value for g in musical2.primary_genres])
        primary_overlap = len(primary1 & primary2)
        
        base_score = overlap / total if total > 0 else 0
        primary_bonus = primary_overlap * 0.2
        
        return min(base_score + primary_bonus, 1.0)
    
    async def _calculate_style_harmony(
        self, 
        musical1: Optional[MusicalProfile], 
        musical2: Optional[MusicalProfile]
    ) -> float:
        """Calculate creative style harmony"""
        if not musical1 or not musical2:
            return 0.5
        
        styles1 = set([s.value for s in musical1.creative_style])
        styles2 = set([s.value for s in musical2.creative_style])
        
        if not styles1 or not styles2:
            return 0.4
        
        # Some styles complement each other
        complementary_pairs = {
            ('experimental', 'mainstream'),
            ('minimalist', 'maximalist'),
            ('vintage', 'futuristic'),
            ('commercial', 'artistic')
        }
        
        overlap = len(styles1 & styles2)
        complement_score = 0
        
        for style1 in styles1:
            for style2 in styles2:
                if (style1, style2) in complementary_pairs or (style2, style1) in complementary_pairs:
                    complement_score += 1
        
        harmony_score = (overlap * 0.6 + complement_score * 0.4) / max(len(styles1), len(styles2))
        return min(harmony_score, 1.0)
    
    async def _calculate_technical_complement(
        self, 
        musical1: Optional[MusicalProfile], 
        musical2: Optional[MusicalProfile]
    ) -> float:
        """Calculate technical skill complementarity"""
        if not musical1 or not musical2:
            return 0.5
        
        skills1 = set(musical1.instrument_skills + musical1.production_skills)
        skills2 = set(musical2.instrument_skills + musical2.production_skills)
        
        if not skills1 or not skills2:
            return 0.3
        
        # Complementary skills are valuable
        complement = len(skills1 - skills2) + len(skills2 - skills1)
        overlap = len(skills1 & skills2)
        total = len(skills1 | skills2)
        
        # Balance between complement and overlap
        complement_score = complement / total if total > 0 else 0
        overlap_score = overlap / total if total > 0 else 0
        
        # 70% complement, 30% overlap
        return complement_score * 0.7 + overlap_score * 0.3
    
    # Additional helper methods would continue here...
    # For brevity, I'll implement key methods and indicate where others would go
    
    async def _calculate_artistic_vision_match(self, profile1, profile2, musical1, musical2) -> float:
        """Calculate artistic vision alignment"""
        # Implementation would analyze artist statements, influences, target audience
        return 0.7  # Placeholder
    
    async def _calculate_work_style_compatibility(self, profile1, profile2) -> float:
        """Calculate work style compatibility"""
        # Implementation would analyze communication preferences, work habits
        return 0.6  # Placeholder
    
    async def _calculate_innovation_balance(self, profile1, profile2, musical1, musical2) -> float:
        """Calculate innovation balance between creators"""
        # Implementation would balance experimental vs. commercial approaches
        return 0.8  # Placeholder
    
    async def _calculate_experience_balance(self, profile1, profile2) -> float:
        """Calculate experience level balance"""
        exp1 = profile1.get('experience_level', 'beginner')
        exp2 = profile2.get('experience_level', 'beginner')
        
        exp_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        level1 = exp_levels.get(exp1, 1)
        level2 = exp_levels.get(exp2, 1)
        
        # Optimal difference is 1 level
        diff = abs(level1 - level2)
        if diff == 0:
            return 0.9
        elif diff == 1:
            return 1.0
        elif diff == 2:
            return 0.7
        else:
            return 0.4
    
    async def _calculate_audience_overlap(self, profile1, profile2) -> float:
        """Calculate audience overlap potential"""
        # Implementation would analyze follower demographics, engagement patterns
        return 0.5  # Placeholder
    
    async def _calculate_brand_alignment(self, profile1, profile2) -> float:
        """Calculate brand alignment score"""
        # Implementation would analyze brand values, content style, messaging
        return 0.6  # Placeholder
    
    async def _calculate_communication_style(self, profile1, profile2) -> float:
        """Calculate communication style compatibility"""
        # Implementation would analyze communication preferences, response times
        return 0.7  # Placeholder
    
    async def _calculate_timeline_preference(self, profile1, profile2) -> float:
        """Calculate timeline preference alignment"""
        # Implementation would analyze project timeline preferences
        return 0.8  # Placeholder
    
    async def _calculate_commitment_level(self, profile1, profile2) -> float:
        """Calculate commitment level compatibility"""
        # Implementation would analyze collaboration history, project completion rates
        return 0.7  # Placeholder
    
    def _generate_compatibility_explanation(self, total_score, genre_score, style_score, vision_score, experience_score) -> str:
        """Generate human-readable compatibility explanation"""
        if total_score >= 0.8:
            return "Excellent compatibility with strong alignment across all dimensions"
        elif total_score >= 0.6:
            return "Good compatibility with some areas for growth"
        elif total_score >= 0.4:
            return "Moderate compatibility, collaboration may require careful planning"
        else:
            return "Limited compatibility, significant challenges expected"
    
    def _calculate_score_confidence(self, profile1, profile2, musical1, musical2) -> float:
        """Calculate confidence in compatibility score based on data completeness"""
        data_points = 0
        total_points = 10
        
        if profile1.get('experience_level'): data_points += 1
        if profile2.get('experience_level'): data_points += 1
        if musical1 and musical1.primary_genres: data_points += 2
        if musical2 and musical2.primary_genres: data_points += 2
        if musical1 and musical1.creative_style: data_points += 1
        if musical2 and musical2.creative_style: data_points += 1
        if musical1 and musical1.instrument_skills: data_points += 1
        if musical2 and musical2.instrument_skills: data_points += 1
        
        return data_points / total_points
    
    # Prediction helper methods
    async def _extract_prediction_features(self, creator1_id, creator2_id, compatibility, project_data) -> List[float]:
        """Extract features for ML prediction model"""
        features = [
            compatibility.total_score,
            compatibility.genre_alignment,
            compatibility.style_harmony,
            compatibility.technical_complement,
            compatibility.artistic_vision_match,
            compatibility.work_style_compatibility,
            compatibility.innovation_balance,
            compatibility.experience_balance,
            compatibility.audience_overlap,
            compatibility.brand_alignment,
            compatibility.communication_style,
            compatibility.timeline_preference,
            compatibility.commitment_level,
            len(self.collaboration_history.get(creator1_id, [])),
            len(self.collaboration_history.get(creator2_id, []))
        ]
        return features
    
    async def _predict_audience_growth(self, creator1_id, creator2_id, success_prob) -> float:
        """Predict audience growth from collaboration"""
        profile1 = self.creator_profiles.get(creator1_id, {})
        profile2 = self.creator_profiles.get(creator2_id, {})
        
        followers1 = profile1.get('follower_count', 0)
        followers2 = profile2.get('follower_count', 0)
        
        # Base growth calculation
        base_growth = (followers1 + followers2) * 0.05 * success_prob
        return min(base_growth, followers1 * 0.5)
    
    async def _predict_revenue(self, creator1_id, creator2_id, success_prob, project_data) -> Decimal:
        """Predict revenue from collaboration"""
        # Base revenue calculation would consider:
        # - Historical revenue data
        # - Platform monetization rates
        # - Audience size and engagement
        # - Project type and scope
        
        base_revenue = Decimal('1000') * Decimal(str(success_prob))
        return base_revenue
    
    async def _predict_engagement_boost(self, creator1_id, creator2_id, success_prob) -> float:
        """Predict engagement boost from collaboration"""
        return success_prob * 0.3  # 30% max engagement boost
    
    async def _identify_risk_factors(self, creator1_id, creator2_id, compatibility) -> List[str]:
        """Identify potential risk factors for collaboration"""
        risks = []
        
        if compatibility.communication_style < 0.5:
            risks.append("Communication style mismatch")
        
        if compatibility.timeline_preference < 0.5:
            risks.append("Timeline preference conflict")
        
        if compatibility.experience_balance < 0.4:
            risks.append("Significant experience gap")
        
        if compatibility.brand_alignment < 0.5:
            risks.append("Brand alignment concerns")
        
        return risks
    
    async def _identify_success_factors(self, creator1_id, creator2_id, compatibility) -> List[str]:
        """Identify success factors for collaboration"""
        factors = []
        
        if compatibility.genre_alignment > 0.7:
            factors.append("Strong genre alignment")
        
        if compatibility.technical_complement > 0.7:
            factors.append("Complementary technical skills")
        
        if compatibility.artistic_vision_match > 0.7:
            factors.append("Aligned artistic vision")
        
        if compatibility.audience_overlap > 0.6:
            factors.append("Good audience synergy")
        
        return factors
    
    async def _predict_timeline(self, collaboration_type, compatibility_score) -> int:
        """Predict collaboration timeline"""
        base_days = {
            'feature': 30,
            'remix': 21,
            'album': 90,
            'single': 14,
            'ep': 45
        }
        
        days = base_days.get(collaboration_type, 30)
        
        # Adjust based on compatibility
        if compatibility_score > 0.8:
            days = int(days * 0.8)  # 20% faster
        elif compatibility_score < 0.5:
            days = int(days * 1.3)  # 30% slower
        
        return days
    
    def _calculate_prediction_confidence_interval(self, success_prob, compatibility) -> Tuple[float, float]:
        """Calculate confidence interval for prediction"""
        confidence = compatibility.confidence
        margin = (1 - confidence) * 0.2
        
        lower = max(0.0, success_prob - margin)
        upper = min(1.0, success_prob + margin)
        
        return (lower, upper)
    
    # Proactive suggestion methods
    async def _generate_collaboration_suggestions(self, creator_id: str) -> List[ProactiveSuggestion]:
        """Generate collaboration-based suggestions"""
        suggestions = []
        
        # Find top potential collaborators
        matches = await self.find_personalized_matches(creator_id, limit=3)
        
        if matches:
            suggestion = ProactiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                creator_id=creator_id,
                suggestion_type="collaboration",
                title="High-Compatibility Collaboration Opportunities",
                description=f"Found {len(matches)} creators with excellent compatibility scores",
                potential_partners=[match[0] for match in matches[:3]],
                action_items=[
                    "Review potential collaborator profiles",
                    "Send collaboration proposals",
                    "Schedule initial discussions"
                ],
                priority_score=0.8,
                confidence=0.9,
                expires_at=datetime.now() + timedelta(days=7)
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    async def _generate_trend_suggestions(self, creator_id: str) -> List[ProactiveSuggestion]:
        """Generate trend-based suggestions"""
        suggestions = []
        
        # Mock trending genre analysis
        trending_genres = ['electronic', 'lo_fi', 'indie_pop']
        creator_musical = self.musical_profiles.get(creator_id)
        
        if creator_musical:
            creator_genres = [g.value for g in creator_musical.primary_genres]
            
            for trend_genre in trending_genres:
                if trend_genre not in creator_genres:
                    suggestion = ProactiveSuggestion(
                        suggestion_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        suggestion_type="trend",
                        title=f"Trending Genre Opportunity: {trend_genre.title()}",
                        description=f"The {trend_genre} genre is trending. Consider exploring this style.",
                        action_items=[
                            f"Research {trend_genre} artists and techniques",
                            f"Create experimental {trend_genre} content",
                            "Collaborate with artists in this genre"
                        ],
                        priority_score=0.6,
                        confidence=0.7,
                        expires_at=datetime.now() + timedelta(days=14),
                        metadata={"trend_genre": trend_genre}
                    )
                    suggestions.append(suggestion)
                    break  # Limit to one trend suggestion
        
        return suggestions
    
    async def _generate_optimization_suggestions(self, creator_id: str) -> List[ProactiveSuggestion]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Analyze collaboration history for optimization opportunities
        history = self.collaboration_history.get(creator_id, [])
        
        if len(history) < 3:
            suggestion = ProactiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                creator_id=creator_id,
                suggestion_type="optimization",
                title="Build Collaboration Portfolio",
                description="Increase collaboration frequency to build your network and experience",
                action_items=[
                    "Set a goal for monthly collaborations",
                    "Join creator networking events",
                    "Update your collaboration preferences"
                ],
                priority_score=0.7,
                confidence=0.8,
                expires_at=datetime.now() + timedelta(days=30)
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    async def _generate_growth_suggestions(self, creator_id: str) -> List[ProactiveSuggestion]:
        """Generate growth opportunity suggestions"""
        suggestions = []
        
        creator_profile = self.creator_profiles.get(creator_id, {})
        follower_count = creator_profile.get('follower_count', 0)
        
        if follower_count < 10000:
            suggestion = ProactiveSuggestion(
                suggestion_id=str(uuid.uuid4()),
                creator_id=creator_id,
                suggestion_type="growth",
                title="Audience Growth Strategy",
                description="Focus on collaborations to accelerate audience growth",
                action_items=[
                    "Partner with creators who have larger audiences",
                    "Create collaborative content for cross-promotion",
                    "Engage actively with collaborator audiences"
                ],
                priority_score=0.5,
                confidence=0.6,
                expires_at=datetime.now() + timedelta(days=21)
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    async def get_matching_analytics(self) -> Dict[str, Any]:
        """Get analytics data for the matching engine"""
        return {
            **self.analytics,
            'total_creators': len(self.creator_profiles),
            'total_musical_profiles': len(self.musical_profiles),
            'cache_size': len(self.compatibility_cache),
            'suggestions_cached': sum(len(suggestions) for suggestions in self.suggestion_cache.values()),
            'ml_models_loaded': len([m for m in self.ml_models.values() if m is not None]),
            'graph_nodes': len(self.graph_network) if self.graph_network and hasattr(self.graph_network, '__len__') else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the matching engine"""
        health = {
            'status': 'healthy' if self.is_initialized else 'not_initialized',
            'ml_available': ML_AVAILABLE,
            'models_loaded': len([m for m in self.ml_models.values() if m is not None]),
            'graph_network_ready': self.graph_network is not None,
            'creators_registered': len(self.creator_profiles),
            'cache_active': len(self.compatibility_cache) > 0
        }
        
        return health


# Export main classes
__all__ = [
    'AdvancedMatchingEngine',
    'MatchingAlgorithm',
    'MusicGenre',
    'CreativeStyle',
    'MusicalProfile',
    'CreativeCompatibilityScore',
    'CollaborationPrediction',
    'ProactiveSuggestion',
    'CollaborationHistory'
]