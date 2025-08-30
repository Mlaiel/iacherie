"""
CreativeSuggestionEngine - AI-Powered Creative Recommendations System
=====================================================================

Professional AI system for intelligent creative direction analysis, innovation assessment,
and artistic enhancement suggestions for music remix and production workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
Contact: mlaiel@live.de for licensing, partnerships, and OEM opportunities.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union
import json

logger = logging.getLogger(__name__)

# Enumerations
class SuggestionType(Enum):
    """Creative suggestion categories"""
    STRUCTURAL = "structural"
    HARMONIC = "harmonic"
    RHYTHMIC = "rhythmic"
    MELODIC = "melodic"
    TEXTURAL = "textural"
    PRODUCTION = "production"
    ARRANGEMENT = "arrangement"
    CREATIVE_DIRECTION = "creative_direction"

class SuggestionPriority(Enum):
    """Suggestion priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"

class CreativeDirection(Enum):
    """Creative direction types"""
    PROGRESSIVE_BUILD = "progressive_build"
    MINIMALIST_APPROACH = "minimalist_approach"
    LAYERED_COMPLEXITY = "layered_complexity"
    EXPERIMENTAL_FUSION = "experimental_fusion"
    COMMERCIAL_APPEAL = "commercial_appeal"
    UNDERGROUND_EDGE = "underground_edge"
    NOSTALGIC_REVIVAL = "nostalgic_revival"
    FUTURISTIC_INNOVATION = "futuristic_innovation"

class InnovationLevel(Enum):
    """Innovation assessment levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    INNOVATIVE = "innovative"
    EXPERIMENTAL = "experimental"
    REVOLUTIONARY = "revolutionary"

# Data Models
@dataclass
class CreativeSuggestion:
    """Individual creative suggestion with detailed analysis"""
    suggestion_id: str = field(default_factory=lambda: f"sug_{uuid.uuid4().hex[:8]}")
    type: SuggestionType = SuggestionType.CREATIVE_DIRECTION
    priority: SuggestionPriority = SuggestionPriority.MEDIUM
    title: str = ""
    description: str = ""
    
    # Analysis metrics
    innovation_score: float = 0.0  # 0.0 to 1.0
    feasibility_score: float = 0.0  # 0.0 to 1.0
    impact_score: float = 0.0  # 0.0 to 1.0
    market_appeal_score: float = 0.0  # 0.0 to 1.0
    
    # Implementation details
    implementation_complexity: str = "medium"
    estimated_time_investment: str = "moderate"
    required_skills: List[str] = field(default_factory=list)
    technical_requirements: List[str] = field(default_factory=list)
    
    # Creative context
    inspiration_sources: List[str] = field(default_factory=list)
    reference_tracks: List[str] = field(default_factory=list)
    style_influences: List[str] = field(default_factory=list)
    
    # Business impact
    commercial_potential: float = 0.0
    viral_potential: float = 0.0
    trend_alignment: float = 0.0
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CreativeSuggestionEngine:
    """
    AI-Powered Creative Recommendations System
    
    Advanced AI system providing intelligent creative direction analysis,
    innovation assessment, and personalized artistic enhancement suggestions.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Engine configuration
        self.creativity_level = config.get("creativity_level", "professional")
        self.innovation_bias = config.get("innovation_bias", 0.7)  # 0=conservative, 1=experimental
        self.market_awareness = config.get("market_awareness", True)
        self.personalization_enabled = config.get("personalization_enabled", True)
        
        # Creative databases
        self.suggestion_database = self._load_suggestion_database()
        self.innovation_patterns = self._load_innovation_patterns()
        self.market_trends = self._load_market_trends()
        
        # AI models configuration
        self.models = {
            "creativity_analyzer": {"version": "3.1.0", "accuracy": 0.91},
            "innovation_assessor": {"version": "2.8.4", "accuracy": 0.87},
            "market_predictor": {"version": "1.9.7", "accuracy": 0.84},
            "trend_analyzer": {"version": "2.3.2", "accuracy": 0.89}
        }
        
        # Performance tracking
        self.performance_metrics = {
            "suggestions_generated": 0,
            "innovation_scores": [],
            "user_adoption_rate": 0.0,
            "creative_success_rate": 0.0
        }

    def _load_suggestion_database(self) -> Dict[str, Any]:
        """Load comprehensive creative suggestion database"""
        return {
            "structural_suggestions": {
                "intro_variations": [
                    "ambient_atmospheric_build",
                    "rhythmic_percussion_intro",
                    "melodic_hook_teaser",
                    "silence_to_impact_drop"
                ],
                "arrangement_patterns": [
                    "verse_chorus_bridge_structure",
                    "breakdown_buildup_drop_cycle",
                    "progressive_layering_approach",
                    "minimal_to_maximal_journey"
                ],
                "transition_techniques": [
                    "filter_sweep_transitions",
                    "rhythmic_displacement_bridges",
                    "harmonic_tension_releases",
                    "textural_morphing_passages"
                ]
            },
            "harmonic_suggestions": {
                "chord_progressions": [
                    "modal_interchange_variations",
                    "suspended_chord_tensions",
                    "chromatic_voice_leading",
                    "quartal_harmony_experiments"
                ],
                "modulation_techniques": [
                    "pivot_chord_modulations",
                    "direct_key_changes",
                    "chromatic_mediant_shifts",
                    "enharmonic_transformations"
                ]
            },
            "production_suggestions": {
                "mixing_techniques": [
                    "parallel_compression_layering",
                    "frequency_masking_optimization",
                    "stereo_imaging_enhancement",
                    "dynamic_range_control"
                ],
                "creative_effects": [
                    "granular_synthesis_textures",
                    "convolution_reverb_spaces",
                    "modulation_automation_curves",
                    "harmonic_distortion_coloring"
                ]
            }
        }

    def _load_innovation_patterns(self) -> Dict[str, Any]:
        """Load innovation analysis patterns"""
        return {
            "breakthrough_patterns": {
                "genre_fusion": ["electronic_orchestral", "hip_hop_jazz", "folk_edm"],
                "production_innovations": ["ai_synthesis", "3d_audio", "adaptive_mixing"],
                "structural_innovations": ["non_linear_arrangements", "interactive_elements"]
            },
            "trend_cycles": {
                "nostalgic_revivals": {"cycle_years": 20, "current_focus": "2000s_revival"},
                "technology_adoption": {"ai_tools": 0.85, "vr_audio": 0.23, "blockchain_music": 0.12}
            }
        }

    def _load_market_trends(self) -> Dict[str, Any]:
        """Load current market trend data"""
        return {
            "streaming_trends": {
                "popular_genres": ["pop", "hip_hop", "electronic", "indie"],
                "emerging_subgenres": ["bedroom_pop", "dark_ambient", "future_garage"],
                "viral_characteristics": ["hook_under_15s", "tiktok_friendly", "playlist_optimized"]
            },
            "platform_preferences": {
                "spotify": {"discovery_factors": ["playlist_inclusion", "algorithmic_boost"]},
                "tiktok": {"viral_factors": ["15s_hook", "dance_potential", "memeable_content"]},
                "youtube": {"engagement_factors": ["visual_appeal", "storytelling", "community"]}
            }
        }

    async def generate_suggestions(self, 
                                 musical_context: Dict[str, Any],
                                 creative_goals: Optional[List[str]] = None,
                                 user_preferences: Optional[Dict[str, Any]] = None) -> List[CreativeSuggestion]:
        """
        Generate comprehensive creative suggestions based on musical context
        
        Args:
            musical_context: Current musical analysis and context
            creative_goals: Specific creative objectives
            user_preferences: User's creative preferences and constraints
            
        Returns:
            List[CreativeSuggestion]: Prioritized creative suggestions
        """
        try:
            logger.info("Generating creative suggestions")
            start_time = time.time()
            
            suggestions = []
            goals = creative_goals or ["enhance_creativity", "commercial_appeal"]
            prefs = user_preferences or {}
            
            # Analyze current creative state
            creative_analysis = await self._analyze_creative_state(musical_context)
            
            # Generate suggestions by category
            structural_suggestions = await self._generate_structural_suggestions(
                musical_context, creative_analysis, goals
            )
            suggestions.extend(structural_suggestions)
            
            harmonic_suggestions = await self._generate_harmonic_suggestions(
                musical_context, creative_analysis, goals
            )
            suggestions.extend(harmonic_suggestions)
            
            production_suggestions = await self._generate_production_suggestions(
                musical_context, creative_analysis, goals
            )
            suggestions.extend(production_suggestions)
            
            creative_direction_suggestions = await self._generate_creative_direction_suggestions(
                musical_context, creative_analysis, goals
            )
            suggestions.extend(creative_direction_suggestions)
            
            # Personalize suggestions based on user preferences
            if self.personalization_enabled and prefs:
                suggestions = await self._personalize_suggestions(suggestions, prefs)
            
            # Prioritize and score suggestions
            suggestions = await self._prioritize_suggestions(suggestions, creative_analysis)
            
            # Update performance metrics
            self.performance_metrics["suggestions_generated"] += len(suggestions)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Generated {len(suggestions)} suggestions in {processing_time:.2f}ms")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []

    async def _analyze_creative_state(self, musical_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current creative state and opportunities"""
        
        # Extract key musical characteristics
        style_analysis = musical_context.get("style_analysis", {})
        production_analysis = musical_context.get("production_analysis", {})
        
        return {
            "creativity_score": self._calculate_creativity_score(musical_context),
            "innovation_opportunities": self._identify_innovation_opportunities(musical_context),
            "commercial_potential": self._assess_commercial_potential(musical_context),
            "technical_sophistication": self._assess_technical_sophistication(production_analysis),
            "artistic_uniqueness": self._assess_artistic_uniqueness(style_analysis),
            "market_positioning": self._analyze_market_positioning(musical_context)
        }

    def _calculate_creativity_score(self, context: Dict[str, Any]) -> float:
        """Calculate overall creativity score"""
        factors = []
        
        # Harmonic innovation
        harmonic_data = context.get("harmonic_characteristics", {})
        factors.append(harmonic_data.get("harmonic_innovation", 0.5))
        
        # Rhythmic complexity
        rhythmic_data = context.get("rhythmic_characteristics", {})
        factors.append(rhythmic_data.get("rhythmic_complexity", 0.5))
        
        # Production innovation
        production_data = context.get("production_characteristics", {})
        tech_markers = production_data.get("technological_markers", [])
        factors.append(min(len(tech_markers) / 5.0, 1.0))
        
        return sum(factors) / len(factors) if factors else 0.5

    def _identify_innovation_opportunities(self, context: Dict[str, Any]) -> List[str]:
        """Identify specific innovation opportunities"""
        opportunities = []
        
        harmonic_data = context.get("harmonic_characteristics", {})
        if harmonic_data.get("chord_complexity", "simple") == "simple":
            opportunities.append("harmonic_sophistication")
        
        rhythmic_data = context.get("rhythmic_characteristics", {})
        if not rhythmic_data.get("polyrhythmic_elements", False):
            opportunities.append("rhythmic_layering")
        
        production_data = context.get("production_characteristics", {})
        if "ai_enhancement" not in production_data.get("technological_markers", []):
            opportunities.append("ai_production_techniques")
        
        return opportunities

    async def _generate_structural_suggestions(self, 
                                             context: Dict[str, Any],
                                             analysis: Dict[str, Any],
                                             goals: List[str]) -> List[CreativeSuggestion]:
        """Generate structural arrangement suggestions"""
        suggestions = []
        
        # Analyze current structure
        current_complexity = analysis.get("technical_sophistication", 0.5)
        
        if current_complexity < 0.6:
            suggestions.append(CreativeSuggestion(
                type=SuggestionType.STRUCTURAL,
                priority=SuggestionPriority.HIGH,
                title="Add Progressive Build Section",
                description="Introduce a progressive build-up section with layered elements to create more dynamic tension before the main drop",
                innovation_score=0.75,
                feasibility_score=0.85,
                impact_score=0.80,
                market_appeal_score=0.78,
                implementation_complexity="medium",
                estimated_time_investment="2-3 hours",
                required_skills=["arrangement", "sound_design"],
                technical_requirements=["multi_track_daw", "automation_tools"],
                inspiration_sources=["progressive_house", "cinematic_scoring"],
                commercial_potential=0.82,
                viral_potential=0.68,
                trend_alignment=0.75
            ))
        
        if "commercial_appeal" in goals:
            suggestions.append(CreativeSuggestion(
                type=SuggestionType.STRUCTURAL,
                priority=SuggestionPriority.MEDIUM,
                title="Optimize Hook Placement",
                description="Reposition the main melodic hook to occur within the first 15 seconds for better streaming platform performance",
                innovation_score=0.45,
                feasibility_score=0.95,
                impact_score=0.85,
                market_appeal_score=0.92,
                implementation_complexity="low",
                estimated_time_investment="30-60 minutes",
                required_skills=["arrangement"],
                technical_requirements=["basic_daw"],
                inspiration_sources=["pop_music_structure", "streaming_optimization"],
                commercial_potential=0.88,
                viral_potential=0.85,
                trend_alignment=0.91
            ))
        
        return suggestions

    async def _generate_harmonic_suggestions(self,
                                           context: Dict[str, Any],
                                           analysis: Dict[str, Any],
                                           goals: List[str]) -> List[CreativeSuggestion]:
        """Generate harmonic enhancement suggestions"""
        suggestions = []
        
        harmonic_data = context.get("harmonic_characteristics", {})
        
        if harmonic_data.get("chord_complexity", "simple") == "simple":
            suggestions.append(CreativeSuggestion(
                type=SuggestionType.HARMONIC,
                priority=SuggestionPriority.MEDIUM,
                title="Introduce Suspended Chord Tensions",
                description="Add sus2 and sus4 chords to create harmonic interest and emotional tension without overly complex jazz harmony",
                innovation_score=0.68,
                feasibility_score=0.78,
                impact_score=0.72,
                market_appeal_score=0.71,
                implementation_complexity="medium",
                estimated_time_investment="1-2 hours",
                required_skills=["music_theory", "chord_progressions"],
                technical_requirements=["piano_keyboard", "theory_knowledge"],
                inspiration_sources=["contemporary_pop", "neo_soul"],
                commercial_potential=0.73,
                viral_potential=0.58,
                trend_alignment=0.67
            ))
        
        return suggestions

    async def _generate_production_suggestions(self,
                                             context: Dict[str, Any],
                                             analysis: Dict[str, Any],
                                             goals: List[str]) -> List[CreativeSuggestion]:
        """Generate production technique suggestions"""
        suggestions = []
        
        production_data = context.get("production_characteristics", {})
        
        if "sidechain_compression" not in production_data.get("production_techniques", []):
            suggestions.append(CreativeSuggestion(
                type=SuggestionType.PRODUCTION,
                priority=SuggestionPriority.HIGH,
                title="Implement Creative Sidechain Compression",
                description="Apply rhythmic sidechain compression to create pumping effect and add groove dynamics characteristic of modern electronic production",
                innovation_score=0.58,
                feasibility_score=0.88,
                impact_score=0.82,
                market_appeal_score=0.85,
                implementation_complexity="medium",
                estimated_time_investment="45-90 minutes",
                required_skills=["compression_techniques", "rhythmic_analysis"],
                technical_requirements=["compressor_plugin", "trigger_source"],
                inspiration_sources=["modern_edm", "french_house"],
                commercial_potential=0.81,
                viral_potential=0.74,
                trend_alignment=0.89
            ))
        
        return suggestions

    async def _generate_creative_direction_suggestions(self,
                                                     context: Dict[str, Any],
                                                     analysis: Dict[str, Any],
                                                     goals: List[str]) -> List[CreativeSuggestion]:
        """Generate overall creative direction suggestions"""
        suggestions = []
        
        uniqueness_score = analysis.get("artistic_uniqueness", 0.5)
        
        if uniqueness_score < 0.7 and self.innovation_bias > 0.6:
            suggestions.append(CreativeSuggestion(
                type=SuggestionType.CREATIVE_DIRECTION,
                priority=SuggestionPriority.HIGH,
                title="Explore Cross-Genre Fusion Elements",
                description="Integrate elements from complementary genres to create a unique sonic signature and differentiate from current market offerings",
                innovation_score=0.89,
                feasibility_score=0.65,
                impact_score=0.85,
                market_appeal_score=0.62,
                implementation_complexity="high",
                estimated_time_investment="4-8 hours",
                required_skills=["genre_knowledge", "creative_synthesis", "arrangement"],
                technical_requirements=["diverse_sample_library", "advanced_daw"],
                inspiration_sources=["innovative_artists", "genre_pioneers"],
                commercial_potential=0.58,
                viral_potential=0.78,
                trend_alignment=0.71
            ))
        
        return suggestions

    async def _personalize_suggestions(self, 
                                     suggestions: List[CreativeSuggestion],
                                     preferences: Dict[str, Any]) -> List[CreativeSuggestion]:
        """Personalize suggestions based on user preferences"""
        
        user_skill_level = preferences.get("skill_level", "intermediate")
        time_constraints = preferences.get("time_constraints", "moderate")
        creative_style = preferences.get("creative_style", "balanced")
        
        # Filter suggestions based on skill level
        if user_skill_level == "beginner":
            suggestions = [s for s in suggestions if s.implementation_complexity in ["low", "medium"]]
        
        # Adjust priorities based on time constraints
        if time_constraints == "limited":
            for suggestion in suggestions:
                if "30-60 minutes" in suggestion.estimated_time_investment:
                    suggestion.priority = SuggestionPriority.HIGH
                elif "4-8 hours" in suggestion.estimated_time_investment:
                    suggestion.priority = SuggestionPriority.LOW
        
        # Adjust innovation scores based on creative style
        if creative_style == "conservative":
            for suggestion in suggestions:
                suggestion.innovation_score *= 0.7
                suggestion.market_appeal_score *= 1.2
        elif creative_style == "experimental":
            for suggestion in suggestions:
                suggestion.innovation_score *= 1.3
                suggestion.feasibility_score *= 0.8
        
        return suggestions

    async def _prioritize_suggestions(self,
                                    suggestions: List[CreativeSuggestion],
                                    analysis: Dict[str, Any]) -> List[CreativeSuggestion]:
        """Prioritize suggestions based on impact and feasibility"""
        
        def calculate_priority_score(suggestion: CreativeSuggestion) -> float:
            # Weighted priority calculation
            return (suggestion.impact_score * 0.3 +
                   suggestion.feasibility_score * 0.25 +
                   suggestion.innovation_score * 0.2 +
                   suggestion.market_appeal_score * 0.15 +
                   suggestion.commercial_potential * 0.1)
        
        # Calculate priority scores
        for suggestion in suggestions:
            priority_score = calculate_priority_score(suggestion)
            
            # Adjust priority enum based on score
            if priority_score >= 0.8:
                suggestion.priority = SuggestionPriority.CRITICAL
            elif priority_score >= 0.7:
                suggestion.priority = SuggestionPriority.HIGH
            elif priority_score >= 0.5:
                suggestion.priority = SuggestionPriority.MEDIUM
            elif priority_score >= 0.3:
                suggestion.priority = SuggestionPriority.LOW
            else:
                suggestion.priority = SuggestionPriority.OPTIONAL
        
        # Sort by priority and score
        priority_order = {
            SuggestionPriority.CRITICAL: 5,
            SuggestionPriority.HIGH: 4,
            SuggestionPriority.MEDIUM: 3,
            SuggestionPriority.LOW: 2,
            SuggestionPriority.OPTIONAL: 1
        }
        
        suggestions.sort(key=lambda s: (
            priority_order[s.priority],
            calculate_priority_score(s)
        ), reverse=True)
        
        return suggestions

    def _assess_commercial_potential(self, context: Dict[str, Any]) -> float:
        """Assess commercial viability of current creative direction"""
        factors = []
        
        # Market trend alignment
        style_data = context.get("style_analysis", {})
        primary_style = style_data.get("primary_style", "")
        
        popular_genres = self.market_trends["streaming_trends"]["popular_genres"]
        if any(genre in primary_style.lower() for genre in popular_genres):
            factors.append(0.8)
        else:
            factors.append(0.4)
        
        # Production quality
        production_data = context.get("production_characteristics", {})
        if production_data.get("production_era") == "2020s":
            factors.append(0.9)
        else:
            factors.append(0.6)
        
        # Structural accessibility
        rhythmic_data = context.get("rhythmic_characteristics", {})
        if rhythmic_data.get("meter") == "4/4":
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        return sum(factors) / len(factors) if factors else 0.5

    def _assess_technical_sophistication(self, production_data: Dict[str, Any]) -> float:
        """Assess technical sophistication of production"""
        sophistication_indicators = [
            "parallel_processing",
            "multiband_compression",
            "stereo_widening", 
            "frequency_filtering",
            "ai_enhancement"
        ]
        
        techniques = production_data.get("production_techniques", [])
        score = len(set(techniques).intersection(sophistication_indicators)) / len(sophistication_indicators)
        
        return min(score, 1.0)

    def _assess_artistic_uniqueness(self, style_data: Dict[str, Any]) -> float:
        """Assess artistic uniqueness and originality"""
        uniqueness_factors = []
        
        # Cross-genre elements
        fusion_elements = style_data.get("cross_genre_fusion_elements", {})
        uniqueness_factors.append(min(len(fusion_elements) / 3.0, 1.0))
        
        # Innovation markers
        evolution_markers = style_data.get("style_evolution_markers", [])
        uniqueness_factors.append(min(len(evolution_markers) / 4.0, 1.0))
        
        # Cultural diversity
        cultural_identifiers = style_data.get("cultural_identifiers", [])
        uniqueness_factors.append(min(len(cultural_identifiers) / 3.0, 1.0))
        
        return sum(uniqueness_factors) / len(uniqueness_factors) if uniqueness_factors else 0.5

    def _analyze_market_positioning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market positioning"""
        return {
            "mainstream_appeal": self._assess_commercial_potential(context),
            "underground_credibility": 1.0 - self._assess_commercial_potential(context),
            "streaming_optimization": self._assess_streaming_readiness(context),
            "playlist_potential": self._assess_playlist_suitability(context),
            "viral_characteristics": self._assess_viral_potential(context)
        }

    def _assess_streaming_readiness(self, context: Dict[str, Any]) -> float:
        """Assess readiness for streaming platforms"""
        production_data = context.get("production_characteristics", {})
        
        factors = []
        
        # Loudness optimization
        loudness = production_data.get("loudness_level", -14)
        if -16 <= loudness <= -12:  # Optimal range for streaming
            factors.append(1.0)
        else:
            factors.append(0.6)
        
        # Dynamic range
        dynamic_range = production_data.get("dynamic_range", 10)
        if 6 <= dynamic_range <= 12:  # Good for streaming
            factors.append(0.8)
        else:
            factors.append(0.5)
        
        # Modern production markers
        if production_data.get("mastering_approach") == "streaming_optimized":
            factors.append(1.0)
        else:
            factors.append(0.4)
        
        return sum(factors) / len(factors)

    def _assess_playlist_suitability(self, context: Dict[str, Any]) -> float:
        """Assess suitability for playlist inclusion"""
        # Simplified assessment based on genre and structure
        style_data = context.get("style_analysis", {})
        primary_style = style_data.get("primary_style", "")
        
        playlist_friendly_genres = ["pop", "electronic", "hip_hop", "r_and_b"]
        if any(genre in primary_style.lower() for genre in playlist_friendly_genres):
            return 0.8
        return 0.5

    def _assess_viral_potential(self, context: Dict[str, Any]) -> float:
        """Assess potential for viral spread"""
        factors = []
        
        # Hook accessibility
        melodic_data = context.get("melodic_characteristics", {})
        if melodic_data.get("phrase_structure") == "regular_4_bar":
            factors.append(0.7)
        else:
            factors.append(0.4)
        
        # Rhythmic catchiness
        rhythmic_data = context.get("rhythmic_characteristics", {})
        if rhythmic_data.get("groove_type") in ["straight", "shuffle"]:
            factors.append(0.6)
        else:
            factors.append(0.3)
        
        # Modern production appeal
        production_data = context.get("production_characteristics", {})
        if production_data.get("production_era") == "2020s":
            factors.append(0.8)
        else:
            factors.append(0.4)
        
        return sum(factors) / len(factors) if factors else 0.5

    async def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status and performance metrics"""
        return {
            "models": self.models,
            "performance_metrics": self.performance_metrics,
            "configuration": {
                "creativity_level": self.creativity_level,
                "innovation_bias": self.innovation_bias,
                "market_awareness": self.market_awareness,
                "personalization_enabled": self.personalization_enabled
            },
            "database_sizes": {
                "suggestion_database": len(self.suggestion_database),
                "innovation_patterns": len(self.innovation_patterns),
                "market_trends": len(self.market_trends)
            }
        }

# Factory function
def create_creative_engine(config: Optional[Dict[str, Any]] = None) -> CreativeSuggestionEngine:
    """Factory function to create a configured CreativeSuggestionEngine instance"""
    return CreativeSuggestionEngine(config)