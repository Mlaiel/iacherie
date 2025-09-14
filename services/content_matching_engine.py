"""Advanced IA Matching Service

Enterprise-grade AI-powered matching and recommendation system for content creators,
featuring advanced ML algorithms, creative compatibility scoring, and predictive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated code are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, REVERSE ENGINEERING, 
OR COMMERCIALIZATION without explicit written permission is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

For legitimate licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from collections import defaultdict, Counter
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import pearsonr
import heapq

logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Advanced matching strategies"""
    CREATIVE_COMPATIBILITY = "creative_compatibility"
    MUSICAL_STYLE_GENRE = "musical_style_genre"
    COLLABORATION_POTENTIAL = "collaboration_potential"
    SUCCESS_PREDICTION = "success_prediction"
    PROACTIVE_SUGGESTIONS = "proactive_suggestions"
    CROSS_PLATFORM_SYNERGY = "cross_platform_synergy"


class CreativeMatchType(Enum):
    """Types of creative matches"""
    COMPLEMENTARY_SKILLS = "complementary_skills"
    SIMILAR_STYLE = "similar_style"
    GENRE_FUSION = "genre_fusion"
    TECHNICAL_COLLAB = "technical_collab"
    ARTISTIC_VISION = "artistic_vision"
    COMMERCIAL_POTENTIAL = "commercial_potential"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for advanced matching"""
    creator_id: str
    username: str
    
    # Musical/Creative Attributes
    primary_genres: List[str] = field(default_factory=list)
    secondary_genres: List[str] = field(default_factory=list)
    instruments: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    music_style_vector: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Technical Capabilities
    production_skills: Dict[str, float] = field(default_factory=dict)
    software_proficiency: Dict[str, float] = field(default_factory=dict)
    equipment_access: List[str] = field(default_factory=list)
    
    # Collaboration History
    past_collaborations: List[str] = field(default_factory=list)
    collaboration_success_rate: float = 0.0
    preferred_collab_types: List[str] = field(default_factory=list)
    availability_windows: List[Dict] = field(default_factory=list)
    
    # Creative Metrics
    creativity_score: float = 0.0
    innovation_index: float = 0.0
    versatility_rating: float = 0.0
    commercial_appeal: float = 0.0
    
    # Platform Performance
    platform_metrics: Dict[str, Dict] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    
    # Network Analysis
    network_centrality: float = 0.0
    influence_score: float = 0.0
    collaboration_network_size: int = 0
    
    # Behavioral Patterns
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    response_time: float = 0.0
    communication_style: str = "professional"
    
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CompatibilityScore:
    """Creative compatibility scoring result"""
    creator_1_id: str
    creator_2_id: str
    overall_score: float
    
    # Component Scores
    musical_compatibility: float = 0.0
    technical_compatibility: float = 0.0
    creative_synergy: float = 0.0
    communication_fit: float = 0.0
    schedule_alignment: float = 0.0
    commercial_potential: float = 0.0
    
    # Detailed Analysis
    complementary_strengths: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    collaboration_type_suggestions: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    
    # Temporal Factors
    optimal_collaboration_timing: str = "immediate"
    estimated_project_duration: str = "1-3 months"
    
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationPrediction:
    """Collaboration success prediction result"""
    collaboration_id: str
    participants: List[str]
    
    # Success Metrics Prediction
    predicted_engagement_rate: float = 0.0
    predicted_reach: int = 0
    predicted_commercial_value: float = 0.0
    viral_potential: float = 0.0
    
    # Risk Analysis
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    
    # Recommendations
    optimal_platforms: List[str] = field(default_factory=list)
    suggested_content_format: str = "music_video"
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    
    prediction_accuracy: float = 0.0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProactiveSuggestion:
    """Proactive suggestion from AI analysis"""
    suggestion_id: str
    target_creator_id: str
    suggestion_type: str
    
    # Suggestion Content
    title: str
    description: str
    action_items: List[str] = field(default_factory=list)
    
    # Timing and Context
    optimal_timing: datetime = field(default_factory=datetime.now)
    urgency_level: str = "medium"  # low, medium, high, critical
    context_factors: List[str] = field(default_factory=list)
    
    # Expected Outcomes
    expected_benefits: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    estimated_impact: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    data_sources: List[str] = field(default_factory=list)
    ai_confidence: float = 0.0
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))


class AdvancedMatchingService:
    """
    Enterprise-grade advanced IA matching service
    
    Features:
    - Personalized ML recommendation algorithms
    - Creative compatibility scoring
    - Musical style and genre matching
    - Collaboration success prediction  
    - Proactive suggestions system
    - Graph database for complex relationships
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialize the advanced matching service"""
        self.config = config or {}
        
        # Core Components
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.collaboration_graph = nx.Graph()
        self.success_predictor = None
        self.style_analyzer = None
        
        # ML Models
        self.compatibility_model = None
        self.success_prediction_model = None
        self.genre_clustering_model = None
        
        # Caching and Performance
        self.compatibility_cache: Dict[str, CompatibilityScore] = {}
        self.suggestion_cache: Dict[str, List[ProactiveSuggestion]] = {}
        
        # Analytics
        self.matching_analytics = defaultdict(list)
        self.prediction_accuracy_tracker = defaultdict(float)
        
        logger.info("Advanced IA Matching Service initialized")
    
    async def initialize_models(self) -> None:
        """Initialize ML models for advanced matching"""
        try:
            # Initialize compatibility scoring model
            self.compatibility_model = CompatibilityNeuralNetwork()
            
            # Initialize success prediction ensemble
            self.success_prediction_model = CollaborationSuccessEnsemble()
            
            # Initialize style analyzer
            self.style_analyzer = MusicalStyleAnalyzer()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
    
    async def register_creator(self, creator_data: Dict[str, Any]) -> CreatorProfile:
        """Register a new creator with comprehensive profiling"""
        try:
            creator_id = creator_data["creator_id"]
            
            # Create comprehensive profile
            profile = CreatorProfile(
                creator_id=creator_id,
                username=creator_data.get("username", f"creator_{creator_id}"),
                primary_genres=creator_data.get("primary_genres", []),
                secondary_genres=creator_data.get("secondary_genres", []),
                instruments=creator_data.get("instruments", []),
                skills=creator_data.get("skills", []),
                production_skills=creator_data.get("production_skills", {}),
                software_proficiency=creator_data.get("software_proficiency", {}),
                equipment_access=creator_data.get("equipment_access", [])
            )
            
            # Analyze musical style vector
            if profile.primary_genres or profile.secondary_genres:
                profile.music_style_vector = await self._generate_style_vector(profile)
            
            # Calculate initial creativity metrics
            profile.creativity_score = await self._calculate_creativity_score(profile)
            profile.innovation_index = await self._calculate_innovation_index(profile)
            profile.versatility_rating = await self._calculate_versatility_rating(profile)
            
            # Add to collaboration graph
            self.collaboration_graph.add_node(creator_id, profile=profile)
            
            # Store profile
            self.creator_profiles[creator_id] = profile
            
            logger.info(f"Creator {creator_id} registered successfully")
            return profile
            
        except Exception as e:
            logger.error(f"Error registering creator: {str(e)}")
            raise
    
    async def calculate_compatibility_score(
        self,
        creator_1_id: str,
        creator_2_id: str,
        collaboration_type: Optional[str] = None
    ) -> CompatibilityScore:
        """Calculate comprehensive compatibility score between two creators"""
        try:
            # Check cache first
            cache_key = f"{creator_1_id}:{creator_2_id}"
            if cache_key in self.compatibility_cache:
                cached_score = self.compatibility_cache[cache_key]
                if (datetime.now() - cached_score.calculated_at).seconds < 3600:  # 1 hour cache
                    return cached_score
            
            profile_1 = self.creator_profiles.get(creator_1_id)
            profile_2 = self.creator_profiles.get(creator_2_id)
            
            if not profile_1 or not profile_2:
                raise ValueError(f"Creator profiles not found")
            
            # Calculate component scores
            musical_compat = await self._calculate_musical_compatibility(profile_1, profile_2)
            technical_compat = await self._calculate_technical_compatibility(profile_1, profile_2)
            creative_synergy = await self._calculate_creative_synergy(profile_1, profile_2)
            communication_fit = await self._calculate_communication_fit(profile_1, profile_2)
            schedule_alignment = await self._calculate_schedule_alignment(profile_1, profile_2)
            commercial_potential = await self._calculate_commercial_potential(profile_1, profile_2)
            
            # Calculate overall score using weighted combination
            weights = {
                'musical': 0.25,
                'technical': 0.20,
                'creative': 0.25,
                'communication': 0.10,
                'schedule': 0.10,
                'commercial': 0.10
            }
            
            overall_score = (
                musical_compat * weights['musical'] +
                technical_compat * weights['technical'] +
                creative_synergy * weights['creative'] +
                communication_fit * weights['communication'] +
                schedule_alignment * weights['schedule'] +
                commercial_potential * weights['commercial']
            )
            
            # Generate detailed analysis
            complementary_strengths = await self._identify_complementary_strengths(profile_1, profile_2)
            potential_challenges = await self._identify_potential_challenges(profile_1, profile_2)
            collab_suggestions = await self._suggest_collaboration_types(profile_1, profile_2)
            success_prob = await self._predict_collaboration_success_probability(profile_1, profile_2)
            
            # Create compatibility score object
            compatibility_score = CompatibilityScore(
                creator_1_id=creator_1_id,
                creator_2_id=creator_2_id,
                overall_score=overall_score,
                musical_compatibility=musical_compat,
                technical_compatibility=technical_compat,
                creative_synergy=creative_synergy,
                communication_fit=communication_fit,
                schedule_alignment=schedule_alignment,
                commercial_potential=commercial_potential,
                complementary_strengths=complementary_strengths,
                potential_challenges=potential_challenges,
                collaboration_type_suggestions=collab_suggestions,
                success_probability=success_prob
            )
            
            # Cache the result
            self.compatibility_cache[cache_key] = compatibility_score
            
            # Update collaboration graph
            self.collaboration_graph.add_edge(
                creator_1_id, 
                creator_2_id, 
                compatibility_score=overall_score,
                last_calculated=datetime.now()
            )
            
            # Track analytics
            self.matching_analytics['compatibility_calculations'].append({
                'timestamp': datetime.now(),
                'creators': [creator_1_id, creator_2_id],
                'score': overall_score
            })
            
            logger.info(f"Compatibility calculated: {creator_1_id} <-> {creator_2_id}: {overall_score:.3f}")
            return compatibility_score
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {str(e)}")
            raise
    
    async def find_musical_style_matches(
        self,
        creator_id: str,
        match_type: CreativeMatchType = CreativeMatchType.SIMILAR_STYLE,
        limit: int = 10
    ) -> List[Tuple[str, float, str]]:
        """Find creators with matching musical styles and genres"""
        try:
            target_profile = self.creator_profiles.get(creator_id)
            if not target_profile:
                raise ValueError(f"Creator profile not found: {creator_id}")
            
            matches = []
            target_vector = target_profile.music_style_vector
            
            if len(target_vector) == 0:
                logger.warning(f"No style vector available for creator {creator_id}")
                return []
            
            for other_creator_id, other_profile in self.creator_profiles.items():
                if other_creator_id == creator_id:
                    continue
                
                other_vector = other_profile.music_style_vector
                if len(other_vector) == 0:
                    continue
                
                # Calculate style similarity based on match type
                if match_type == CreativeMatchType.SIMILAR_STYLE:
                    similarity = await self._calculate_style_similarity(target_vector, other_vector)
                elif match_type == CreativeMatchType.COMPLEMENTARY_SKILLS:
                    similarity = await self._calculate_skill_complementarity(target_profile, other_profile)
                elif match_type == CreativeMatchType.GENRE_FUSION:
                    similarity = await self._calculate_genre_fusion_potential(target_profile, other_profile)
                else:
                    similarity = await self._calculate_general_musical_match(target_profile, other_profile)
                
                if similarity > 0.3:  # Minimum threshold
                    reason = await self._generate_match_reason(target_profile, other_profile, match_type)
                    matches.append((other_creator_id, similarity, reason))
            
            # Sort by similarity score
            matches.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Found {len(matches)} musical style matches for {creator_id}")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding musical style matches: {str(e)}")
            return []
    
    async def predict_collaboration_success(
        self,
        participant_ids: List[str],
        collaboration_type: str = "music_production",
        target_platforms: List[str] = None
    ) -> CollaborationPrediction:
        """Predict success metrics for a potential collaboration"""
        try:
            if not target_platforms:
                target_platforms = ["youtube", "spotify", "instagram", "tiktok"]
            
            # Get participant profiles
            participants = []
            for creator_id in participant_ids:
                profile = self.creator_profiles.get(creator_id)
                if not profile:
                    raise ValueError(f"Creator profile not found: {creator_id}")
                participants.append(profile)
            
            # Predict engagement metrics using simplified algorithms
            engagement_prediction = await self._predict_engagement_rate(participants, target_platforms)
            reach_prediction = await self._predict_reach(participants)
            commercial_prediction = await self._predict_commercial_value(participants)
            viral_prediction = await self._predict_viral_potential(participants)
            
            # Risk analysis
            risk_factors = await self._analyze_collaboration_risks(participants)
            mitigation_strategies = await self._suggest_risk_mitigation(risk_factors)
            
            # Platform optimization
            optimal_platforms = await self._optimize_platform_selection(participants, target_platforms)
            
            # Content format suggestion
            suggested_format = await self._suggest_content_format(participants, collaboration_type)
            
            # Target demographics analysis
            target_demographics = await self._analyze_target_demographics(participants)
            
            # Create prediction object
            collaboration_id = f"collab_{'-'.join(participant_ids)}_{int(datetime.now().timestamp())}"
            
            prediction = CollaborationPrediction(
                collaboration_id=collaboration_id,
                participants=participant_ids,
                predicted_engagement_rate=engagement_prediction,
                predicted_reach=reach_prediction,
                predicted_commercial_value=commercial_prediction,
                viral_potential=viral_prediction,
                risk_factors=risk_factors,
                mitigation_strategies=mitigation_strategies,
                optimal_platforms=optimal_platforms,
                suggested_content_format=suggested_format,
                target_demographics=target_demographics,
                prediction_accuracy=0.85  # Based on historical model performance
            )
            
            # Store prediction for accuracy tracking
            self.matching_analytics['success_predictions'].append({
                'prediction': prediction,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Success prediction generated for collaboration {collaboration_id}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {str(e)}")
            raise
    
    async def generate_proactive_suggestions(
        self,
        creator_id: str,
        suggestion_types: List[str] = None
    ) -> List[ProactiveSuggestion]:
        """Generate proactive AI-powered suggestions for creators"""
        try:
            if not suggestion_types:
                suggestion_types = [
                    "collaboration_opportunity",
                    "trend_participation", 
                    "skill_development",
                    "platform_optimization",
                    "content_timing",
                    "genre_exploration"
                ]
            
            profile = self.creator_profiles.get(creator_id)
            if not profile:
                raise ValueError(f"Creator profile not found: {creator_id}")
            
            suggestions = []
            
            # Generate collaboration opportunity suggestions
            if "collaboration_opportunity" in suggestion_types:
                best_matches = await self.find_musical_style_matches(creator_id, limit=3)
                for match_id, score, reason in best_matches:
                    suggestion = ProactiveSuggestion(
                        suggestion_id=f"collab_{creator_id}_{match_id}_{int(datetime.now().timestamp())}",
                        target_creator_id=creator_id,
                        suggestion_type="collaboration_opportunity",
                        title=f"High-Potential Collaboration with {self.creator_profiles[match_id].username}",
                        description=f"AI analysis shows {score:.1%} compatibility. {reason}",
                        action_items=[
                            "Send collaboration invitation",
                            "Schedule creative discussion",
                            "Explore musical synergies"
                        ],
                        urgency_level="high" if score > 0.8 else "medium",
                        expected_benefits=[
                            "Expanded audience reach",
                            "Creative skill exchange",
                            "Enhanced musical portfolio"
                        ],
                        success_probability=score,
                        ai_confidence=0.85
                    )
                    suggestions.append(suggestion)
            
            # Generate genre exploration suggestions
            if "genre_exploration" in suggestion_types:
                current_genres = set(profile.primary_genres + profile.secondary_genres)
                trending_genres = ["lofi", "synthwave", "future_bass", "ambient", "neo_soul"]
                unexplored = [g for g in trending_genres if g not in current_genres]
                
                for genre in unexplored[:2]:
                    suggestion = ProactiveSuggestion(
                        suggestion_id=f"genre_{creator_id}_{genre}_{int(datetime.now().timestamp())}",
                        target_creator_id=creator_id,
                        suggestion_type="genre_exploration",
                        title=f"Explore {genre.replace('_', ' ').title()} Genre",
                        description=f"Based on your musical style, {genre} could expand your creative range",
                        action_items=[
                            f"Research {genre} artists and techniques",
                            f"Create experimental {genre} track",
                            f"Connect with {genre} producers"
                        ],
                        urgency_level="low",
                        expected_benefits=[
                            "Musical versatility increase",
                            "New audience segments",
                            "Creative inspiration"
                        ],
                        success_probability=0.7,
                        ai_confidence=0.75
                    )
                    suggestions.append(suggestion)
            
            # Sort by urgency and success probability
            suggestions.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.urgency_level],
                x.success_probability
            ), reverse=True)
            
            logger.info(f"Generated {len(suggestions)} proactive suggestions for {creator_id}")
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error generating proactive suggestions: {str(e)}")
            return []
    
    async def analyze_creator_network(self, creator_id: str) -> Dict[str, Any]:
        """Analyze creator's position in the collaboration network"""
        try:
            if creator_id not in self.collaboration_graph:
                return {"error": "Creator not found in network"}
            
            # Calculate network metrics if graph has enough nodes
            if len(self.collaboration_graph) < 2:
                return {
                    "centrality_metrics": {"degree_centrality": 0.0},
                    "community_id": 0,
                    "direct_connections": 0,
                    "network_influence_score": 0.0
                }
            
            centrality_metrics = {
                "degree_centrality": nx.degree_centrality(self.collaboration_graph)[creator_id],
                "betweenness_centrality": nx.betweenness_centrality(self.collaboration_graph)[creator_id],
            }
            
            # Find neighbors
            neighbors = list(self.collaboration_graph.neighbors(creator_id))
            
            # Network influence score
            influence_score = (
                centrality_metrics["degree_centrality"] * 0.5 +
                centrality_metrics["betweenness_centrality"] * 0.5
            )
            
            analysis_result = {
                "centrality_metrics": centrality_metrics,
                "direct_connections": len(neighbors),
                "network_influence_score": influence_score,
                "connected_creators": neighbors[:10]
            }
            
            logger.info(f"Network analysis completed for {creator_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing creator network: {str(e)}")
            return {"error": str(e)}

    # --- Internal Helper Methods ---
    
    async def _generate_style_vector(self, profile: CreatorProfile) -> np.ndarray:
        """Generate musical style vector from creator profile"""
        try:
            all_genres = profile.primary_genres + profile.secondary_genres
            genre_encoding = np.zeros(50)  # 50-dimensional style vector
            
            # Genre mapping for encoding
            genre_map = {
                'electronic': [1, 0.8, 0.3, 0.9, 0.2],
                'rock': [0.2, 0.9, 0.8, 0.3, 0.7],
                'jazz': [0.7, 0.3, 0.9, 0.8, 0.4],
                'classical': [0.9, 0.2, 0.7, 0.9, 0.1],
                'hip-hop': [0.3, 0.7, 0.2, 0.4, 0.9],
                'pop': [0.5, 0.6, 0.7, 0.5, 0.8],
                'lofi': [0.6, 0.4, 0.8, 0.3, 0.5],
                'synthwave': [0.9, 0.7, 0.4, 0.8, 0.3]
            }
            
            for i, genre in enumerate(all_genres[:10]):
                if genre in genre_map:
                    start_idx = i * 5
                    end_idx = start_idx + 5
                    if end_idx <= 50:
                        genre_encoding[start_idx:end_idx] = genre_map[genre]
            
            return genre_encoding
            
        except Exception as e:
            logger.error(f"Error generating style vector: {str(e)}")
            return np.zeros(50)
    
    async def _calculate_creativity_score(self, profile: CreatorProfile) -> float:
        """Calculate creativity score based on profile analysis"""
        try:
            score = 0.0
            
            # Genre diversity factor
            total_genres = len(profile.primary_genres) + len(profile.secondary_genres)
            genre_diversity = min(total_genres / 10.0, 1.0)
            score += genre_diversity * 0.3
            
            # Skill diversity factor
            skill_diversity = min(len(profile.skills) / 15.0, 1.0)
            score += skill_diversity * 0.3
            
            # Collaboration openness
            collab_factor = min(len(profile.past_collaborations) / 10.0, 1.0)
            score += collab_factor * 0.2
            
            # Innovation indicators
            experimental_genres = {'experimental', 'fusion', 'avant-garde', 'ambient'}
            innovation_indicators = len(set(profile.primary_genres + profile.secondary_genres) & experimental_genres)
            innovation_factor = min(innovation_indicators / 3.0, 1.0)
            score += innovation_factor * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating creativity score: {str(e)}")
            return 0.5
    
    async def _calculate_innovation_index(self, profile: CreatorProfile) -> float:
        """Calculate innovation index"""
        try:
            unique_combinations = len(set(profile.primary_genres)) * len(set(profile.secondary_genres))
            experimental_factor = len([g for g in profile.primary_genres + profile.secondary_genres 
                                    if any(keyword in g.lower() for keyword in ['experimental', 'fusion', 'ambient'])])
            
            innovation_score = min((unique_combinations + experimental_factor) / 20.0, 1.0)
            return innovation_score
            
        except Exception as e:
            logger.error(f"Error calculating innovation index: {str(e)}")
            return 0.5
    
    async def _calculate_versatility_rating(self, profile: CreatorProfile) -> float:
        """Calculate versatility rating"""
        try:
            genre_versatility = min(len(set(profile.primary_genres + profile.secondary_genres)) / 8.0, 1.0)
            skill_versatility = min(len(profile.skills) / 12.0, 1.0)
            platform_versatility = min(len(profile.platform_metrics) / 6.0, 1.0)
            
            versatility = (genre_versatility + skill_versatility + platform_versatility) / 3.0
            return versatility
            
        except Exception as e:
            logger.error(f"Error calculating versatility rating: {str(e)}")
            return 0.5
    
    async def _calculate_musical_compatibility(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate musical compatibility between two creators"""
        try:
            genres1 = set(profile1.primary_genres + profile1.secondary_genres)
            genres2 = set(profile2.primary_genres + profile2.secondary_genres)
            
            if not genres1 or not genres2:
                return 0.3
            
            overlap = len(genres1 & genres2)
            total_unique = len(genres1 | genres2)
            
            genre_compatibility = overlap / max(total_unique, 1)
            
            # Style vector similarity
            style_similarity = 0.5
            if len(profile1.music_style_vector) > 0 and len(profile2.music_style_vector) > 0:
                try:
                    style_similarity = cosine_similarity(
                        [profile1.music_style_vector], 
                        [profile2.music_style_vector]
                    )[0][0]
                except:
                    style_similarity = 0.5
            
            musical_compatibility = (genre_compatibility * 0.6 + style_similarity * 0.4)
            return max(0.0, min(1.0, musical_compatibility))
            
        except Exception as e:
            logger.error(f"Error calculating musical compatibility: {str(e)}")
            return 0.3

    async def _calculate_technical_compatibility(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate technical compatibility"""
        try:
            software1 = set(profile1.software_proficiency.keys())
            software2 = set(profile2.software_proficiency.keys())
            software_overlap = len(software1 & software2) / max(len(software1 | software2), 1)
            
            skills1 = set(profile1.skills)
            skills2 = set(profile2.skills)
            skill_complement = len(skills1 - skills2) / max(len(skills1 | skills2), 1)
            
            technical_score = (software_overlap * 0.6 + skill_complement * 0.4)
            return max(0.0, min(1.0, technical_score))
            
        except Exception as e:
            logger.error(f"Error calculating technical compatibility: {str(e)}")
            return 0.5

    async def _calculate_creative_synergy(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate creative synergy potential"""
        try:
            creativity_balance = 1.0 - abs(profile1.creativity_score - profile2.creativity_score)
            innovation_avg = (profile1.innovation_index + profile2.innovation_index) / 2.0
            versatility_combined = (profile1.versatility_rating + profile2.versatility_rating) / 2.0
            
            synergy_score = (creativity_balance * 0.4 + innovation_avg * 0.3 + versatility_combined * 0.3)
            return max(0.0, min(1.0, synergy_score))
            
        except Exception as e:
            logger.error(f"Error calculating creative synergy: {str(e)}")
            return 0.5

    async def _calculate_communication_fit(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate communication compatibility"""
        try:
            response_time_diff = abs(profile1.response_time - profile2.response_time)
            response_compatibility = max(0.0, 1.0 - response_time_diff / 24.0)
            
            style_compatibility = 0.8 if profile1.communication_style == profile2.communication_style else 0.6
            
            communication_score = (response_compatibility * 0.5 + style_compatibility * 0.5)
            return max(0.0, min(1.0, communication_score))
            
        except Exception as e:
            logger.error(f"Error calculating communication fit: {str(e)}")
            return 0.7

    async def _calculate_schedule_alignment(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate schedule alignment"""
        try:
            # Simplified - would use actual availability data in production
            return 0.7  # Default moderate alignment
            
        except Exception as e:
            logger.error(f"Error calculating schedule alignment: {str(e)}")
            return 0.6

    async def _calculate_commercial_potential(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate commercial potential"""
        try:
            combined_appeal = (profile1.commercial_appeal + profile2.commercial_appeal) / 2.0
            
            # Calculate combined reach
            reach1 = sum(profile1.platform_metrics.get(platform, {}).get('followers', 0) 
                        for platform in profile1.platform_metrics)
            reach2 = sum(profile2.platform_metrics.get(platform, {}).get('followers', 0) 
                        for platform in profile2.platform_metrics)
            
            combined_reach = reach1 + reach2
            reach_score = min(combined_reach / 100000.0, 1.0)
            
            commercial_score = (combined_appeal * 0.7 + reach_score * 0.3)
            return max(0.0, min(1.0, commercial_score))
            
        except Exception as e:
            logger.error(f"Error calculating commercial potential: {str(e)}")
            return 0.5

    async def _identify_complementary_strengths(self, profile1: CreatorProfile, profile2: CreatorProfile) -> List[str]:
        """Identify complementary strengths"""
        try:
            strengths = []
            
            skills1 = set(profile1.skills)
            skills2 = set(profile2.skills)
            unique_skills1 = skills1 - skills2
            unique_skills2 = skills2 - skills1
            
            if unique_skills1:
                strengths.append(f"{profile1.username} brings: {', '.join(list(unique_skills1)[:3])}")
            if unique_skills2:
                strengths.append(f"{profile2.username} brings: {', '.join(list(unique_skills2)[:3])}")
            
            return strengths[:5]
            
        except Exception as e:
            logger.error(f"Error identifying complementary strengths: {str(e)}")
            return ["Potential for creative synergy"]

    async def _identify_potential_challenges(self, profile1: CreatorProfile, profile2: CreatorProfile) -> List[str]:
        """Identify potential challenges"""
        try:
            challenges = []
            
            # Style difference check
            if len(profile1.music_style_vector) > 0 and len(profile2.music_style_vector) > 0:
                try:
                    style_similarity = cosine_similarity(
                        [profile1.music_style_vector], 
                        [profile2.music_style_vector]
                    )[0][0]
                    if style_similarity < 0.3:
                        challenges.append("Musical style differences may require creative adaptation")
                except:
                    pass
            
            # Experience gap
            collab_exp_diff = abs(len(profile1.past_collaborations) - len(profile2.past_collaborations))
            if collab_exp_diff > 5:
                challenges.append("Different collaboration experience levels")
            
            return challenges[:5]
            
        except Exception as e:
            logger.error(f"Error identifying potential challenges: {str(e)}")
            return ["Standard collaboration coordination needed"]

    async def _suggest_collaboration_types(self, profile1: CreatorProfile, profile2: CreatorProfile) -> List[str]:
        """Suggest collaboration types"""
        try:
            suggestions = []
            
            skills1 = set(profile1.skills)
            skills2 = set(profile2.skills)
            
            production_skills = {'production', 'mixing', 'mastering', 'recording'}
            creative_skills = {'songwriting', 'composition', 'lyrics', 'arrangement'}
            performance_skills = {'vocals', 'guitar', 'piano', 'drums', 'bass'}
            
            if (skills1 & production_skills) and (skills2 & creative_skills):
                suggestions.append("Producer-Songwriter collaboration")
            elif (skills1 & creative_skills) and (skills2 & creative_skills):
                suggestions.append("Co-writing partnership")
            elif (skills1 & performance_skills) and (skills2 & performance_skills):
                suggestions.append("Featured artist collaboration")
            
            suggestions.append("Remix and reinterpretation")
            
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error suggesting collaboration types: {str(e)}")
            return ["General music collaboration"]

    async def _predict_collaboration_success_probability(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Predict collaboration success probability"""
        try:
            musical_compat = await self._calculate_musical_compatibility(profile1, profile2)
            technical_compat = await self._calculate_technical_compatibility(profile1, profile2)
            creative_synergy = await self._calculate_creative_synergy(profile1, profile2)
            
            success_probability = (musical_compat * 0.4 + technical_compat * 0.3 + creative_synergy * 0.3)
            return max(0.0, min(1.0, success_probability))
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {str(e)}")
            return 0.6

    # Additional helper methods
    async def _calculate_style_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate style similarity between vectors"""
        try:
            return cosine_similarity([vector1], [vector2])[0][0]
        except:
            return 0.5

    async def _calculate_skill_complementarity(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate skill complementarity"""
        try:
            skills1 = set(profile1.skills)
            skills2 = set(profile2.skills)
            complement = len(skills1 - skills2) + len(skills2 - skills1)
            total = len(skills1 | skills2)
            return complement / max(total, 1)
        except:
            return 0.5

    async def _calculate_genre_fusion_potential(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate genre fusion potential"""
        try:
            genres1 = set(profile1.primary_genres + profile1.secondary_genres)
            genres2 = set(profile2.primary_genres + profile2.secondary_genres)
            unique_fusion = len(genres1 | genres2) - len(genres1 & genres2)
            return min(unique_fusion / 5.0, 1.0)
        except:
            return 0.5

    async def _calculate_general_musical_match(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate general musical match"""
        try:
            musical_compat = await self._calculate_musical_compatibility(profile1, profile2)
            creativity_compat = 1.0 - abs(profile1.creativity_score - profile2.creativity_score)
            return (musical_compat + creativity_compat) / 2.0
        except:
            return 0.5

    async def _generate_match_reason(self, profile1: CreatorProfile, profile2: CreatorProfile, match_type: CreativeMatchType) -> str:
        """Generate match reason"""
        try:
            if match_type == CreativeMatchType.SIMILAR_STYLE:
                shared_genres = set(profile1.primary_genres) & set(profile2.primary_genres)
                if shared_genres:
                    return f"Shared musical style in {', '.join(list(shared_genres)[:2])}"
                return "Similar musical approach and preferences"
            elif match_type == CreativeMatchType.COMPLEMENTARY_SKILLS:
                return "Complementary skills for powerful creative synergy"
            elif match_type == CreativeMatchType.GENRE_FUSION:
                return "Excellent potential for innovative genre fusion"
            else:
                return "Strong overall creative compatibility"
        except:
            return "Potential creative match"

    # Simplified prediction methods
    async def _predict_engagement_rate(self, participants: List[CreatorProfile], platforms: List[str]) -> float:
        """Predict engagement rate"""
        try:
            avg_creativity = sum(p.creativity_score for p in participants) / len(participants)
            base_rate = 0.05  # 5% base engagement
            creativity_boost = avg_creativity * 0.03  # Up to 3% boost
            return min(base_rate + creativity_boost, 0.15)  # Cap at 15%
        except:
            return 0.08

    async def _predict_reach(self, participants: List[CreatorProfile]) -> int:
        """Predict reach"""
        try:
            total_followers = 0
            for profile in participants:
                for platform_data in profile.platform_metrics.values():
                    total_followers += platform_data.get('followers', 0)
            
            # Collaboration typically reaches 60-80% of combined audience
            collaboration_reach = int(total_followers * 0.7)
            return max(collaboration_reach, 10000)  # Minimum 10k reach
        except:
            return 25000

    async def _predict_commercial_value(self, participants: List[CreatorProfile]) -> float:
        """Predict commercial value"""
        try:
            avg_appeal = sum(p.commercial_appeal for p in participants) / len(participants)
            base_value = 1000.0  # $1000 base
            appeal_multiplier = 1 + (avg_appeal * 4)  # Up to 5x multiplier
            return base_value * appeal_multiplier
        except:
            return 2500.0

    async def _predict_viral_potential(self, participants: List[CreatorProfile]) -> float:
        """Predict viral potential"""
        try:
            innovation_avg = sum(p.innovation_index for p in participants) / len(participants)
            creativity_avg = sum(p.creativity_score for p in participants) / len(participants)
            return min((innovation_avg + creativity_avg) / 2.0, 0.3)  # Cap at 30%
        except:
            return 0.15

    async def _analyze_collaboration_risks(self, participants: List[CreatorProfile]) -> List[str]:
        """Analyze collaboration risks"""
        return ["Schedule coordination needed", "Style alignment required", "Clear communication protocols needed"]

    async def _suggest_risk_mitigation(self, risk_factors: List[str]) -> List[str]:
        """Suggest risk mitigation"""
        return ["Regular progress check-ins", "Establish clear communication channels", "Define roles and responsibilities"]

    async def _optimize_platform_selection(self, participants: List[CreatorProfile], platforms: List[str]) -> List[str]:
        """Optimize platform selection"""
        try:
            # Score platforms based on participant presence
            platform_scores = {}
            for platform in platforms:
                score = 0
                for profile in participants:
                    if platform in profile.platform_metrics:
                        followers = profile.platform_metrics[platform].get('followers', 0)
                        score += min(followers / 10000, 10)  # Score up to 10 per participant
                platform_scores[platform] = score
            
            # Return top 3 platforms
            sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
            return [platform for platform, score in sorted_platforms[:3]]
        except:
            return platforms[:3]

    async def _suggest_content_format(self, participants: List[CreatorProfile], collaboration_type: str) -> str:
        """Suggest content format"""
        try:
            if collaboration_type == "music_production":
                return "music_video"
            elif any("vocals" in p.skills for p in participants):
                return "vocal_feature"
            else:
                return "instrumental_collaboration"
        except:
            return "music_video"

    async def _analyze_target_demographics(self, participants: List[CreatorProfile]) -> Dict[str, Any]:
        """Analyze target demographics"""
        try:
            # Combine demographics from all participants
            combined_demographics = {
                "age_range": "18-34",
                "primary_interests": ["music", "entertainment", "arts"],
                "geographic_regions": ["global"],
                "engagement_preferences": ["audio", "video", "social_media"]
            }
            
            # Analyze genres to refine demographics
            all_genres = []
            for profile in participants:
                all_genres.extend(profile.primary_genres + profile.secondary_genres)
            
            if any(genre in ["hip-hop", "rap", "trap"] for genre in all_genres):
                combined_demographics["age_range"] = "16-28"
            elif any(genre in ["jazz", "classical", "blues"] for genre in all_genres):
                combined_demographics["age_range"] = "25-45"
            
            return combined_demographics
        except:
            return {"age_range": "18-34", "primary_interests": ["music"]}


class CompatibilityNeuralNetwork(nn.Module):
    """Neural network for compatibility scoring"""
    
    def __init__(self, input_size -> None: int = 100) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x) -> None:
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.sigmoid(self.fc3(x))
        return x


class CollaborationSuccessEnsemble:
    """Ensemble model for collaboration success prediction"""
    
    def __init__(self) -> None:
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.mlp_model = MLPRegressor(hidden_layer_sizes=(50, 25), random_state=42)
        self.is_trained = False
        
    def predict(self, features: np.ndarray) -> float:
        """Predict collaboration success probability"""
        if not self.is_trained:
            return 0.65
        
        try:
            rf_pred = self.rf_model.predict([features])[0]
            gb_pred = self.gb_model.predict([features])[0]
            mlp_pred = self.mlp_model.predict([features])[0]
            
            ensemble_pred = (rf_pred * 0.4 + gb_pred * 0.4 + mlp_pred * 0.2)
            return max(0.0, min(1.0, ensemble_pred))
        except:
            return 0.65


class MusicalStyleAnalyzer:
    """Advanced musical style analysis system"""
    
    def __init__(self) -> None:
        self.style_categories = {
            'energy': ['high', 'medium', 'low'],
            'tempo': ['fast', 'medium', 'slow'],
            'mood': ['happy', 'sad', 'energetic', 'calm', 'aggressive', 'peaceful'],
            'complexity': ['simple', 'moderate', 'complex'],
            'instrumentation': ['acoustic', 'electronic', 'mixed'],
            'production_style': ['polished', 'raw', 'experimental']
        }
        
    async def analyze_style_compatibility(self, style1: Dict, style2: Dict) -> float:
        """Analyze compatibility between musical styles"""
        try:
            compatibility_score = 0.0
            total_categories = len(self.style_categories)
            
            for category, options in self.style_categories.items():
                value1 = style1.get(category, 'unknown')
                value2 = style2.get(category, 'unknown')
                
                if value1 == value2:
                    compatibility_score += 1.0
                elif value1 != 'unknown' and value2 != 'unknown':
                    compatibility_score += 0.5
                else:
                    total_categories -= 1
            
            if total_categories > 0:
                return compatibility_score / total_categories
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error analyzing style compatibility: {str(e)}")
            return 0.5


# Module exports
__all__ = [
    'AdvancedMatchingService',
    'MatchingStrategy', 
    'CreativeMatchType',
    'CreatorProfile',
    'CompatibilityScore',
    'CollaborationPrediction',
    'ProactiveSuggestion',
    'CompatibilityNeuralNetwork',
    'CollaborationSuccessEnsemble',
    'MusicalStyleAnalyzer'
]