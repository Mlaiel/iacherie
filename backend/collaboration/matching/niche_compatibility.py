"""Niche Compatibility Module - Advanced Niche and Category Matching System
==========================================================================

Sophisticated niche analysis and category compatibility system for optimal creator
matching based on content categories, audience niches, and creative specializations.

This module implements:
- Multi-dimensional niche analysis
- Category overlap detection
- Niche compatibility scoring
- Audience segment matching
- Creative specialization alignment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd

logger = logging.getLogger(__name__)


class NicheCategory(Enum):
    """Main niche categories for creator classification"""
    MUSIC = "music"
    VIDEO = "video"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    FITNESS = "fitness"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    BUSINESS = "business"
    ART = "art"
    COMEDY = "comedy"
    NEWS = "news"
    SCIENCE = "science"


class CompatibilityType(Enum):
    """Types of niche compatibility"""
    PERFECT_MATCH = "perfect_match"
    COMPLEMENTARY = "complementary"
    ADJACENT = "adjacent"
    CROSSOVER = "crossover"
    EXPERIMENTAL = "experimental"
    INCOMPATIBLE = "incompatible"


@dataclass
class NicheProfile:
    """Comprehensive niche profile for a creator"""
    creator_id: str
    primary_niches: List[NicheCategory]
    secondary_niches: List[NicheCategory]
    content_tags: List[str]
    audience_segments: Dict[str, float]  # segment -> percentage
    specializations: List[str]
    content_style: Dict[str, float]  # style attributes
    niche_authority: Dict[NicheCategory, float]  # niche -> authority score
    cross_niche_experience: Dict[Tuple[NicheCategory, NicheCategory], float]
    niche_evolution: List[Dict[str, Any]]  # historical niche changes
    engagement_by_niche: Dict[NicheCategory, Dict[str, float]]  # niche -> metrics
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class NicheCompatibilityResult:
    """Result of niche compatibility analysis"""
    creator_a_id: str
    creator_b_id: str
    overall_compatibility: float
    compatibility_type: CompatibilityType
    niche_overlap_score: float
    audience_alignment_score: float
    content_synergy_score: float
    crossover_potential: float
    collaboration_opportunities: List[Dict[str, Any]]
    risk_factors: List[str]
    success_probability: float
    recommended_project_types: List[str]
    niche_specific_scores: Dict[NicheCategory, float]
    detailed_analysis: Dict[str, Any]
    confidence_score: float
    analyzed_at: datetime = None
    
    def __post_init__(self):
        if self.analyzed_at is None:
            self.analyzed_at = datetime.now(timezone.utc)


@dataclass
class NicheInsights:
    """Insights and recommendations for niche optimization"""
    creator_id: str
    current_niche_strength: Dict[NicheCategory, float]
    growth_opportunities: List[Dict[str, Any]]
    market_gaps: List[str]
    trending_niches: List[NicheCategory]
    optimal_collaborations: List[str]
    niche_expansion_recommendations: List[Dict[str, Any]]
    audience_development_strategies: List[str]
    content_gap_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now(timezone.utc)


class NicheCompatibilityEngine:
    """Advanced niche compatibility analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the niche compatibility engine"""
        self.config = config or {}
        self.compatibility_threshold = self.config.get('compatibility_threshold', 0.7)
        self.niche_weights = self._init_niche_weights()
        self.content_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.niche_clusters = {}
        self.market_trends = {}
        
        logger.info("🎯 Niche Compatibility Engine initialized")
    
    def _init_niche_weights(self) -> Dict[str, float]:
        """Initialize weights for different compatibility factors"""
        return {
            'niche_overlap': 0.3,
            'audience_alignment': 0.25,
            'content_synergy': 0.2,
            'crossover_potential': 0.15,
            'market_trends': 0.1
        }
    
    async def analyze_compatibility(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> NicheCompatibilityResult:
        """Analyze niche compatibility between two creators"""
        try:
            logger.info(f"🔍 Analyzing niche compatibility: {profile_a.creator_id} + {profile_b.creator_id}")
            
            # Calculate different compatibility dimensions
            niche_overlap = await self._calculate_niche_overlap(profile_a, profile_b)
            audience_alignment = await self._calculate_audience_alignment(profile_a, profile_b)
            content_synergy = await self._calculate_content_synergy(profile_a, profile_b)
            crossover_potential = await self._calculate_crossover_potential(profile_a, profile_b)
            
            # Calculate overall compatibility
            overall_compatibility = (
                niche_overlap * self.niche_weights['niche_overlap'] +
                audience_alignment * self.niche_weights['audience_alignment'] +
                content_synergy * self.niche_weights['content_synergy'] +
                crossover_potential * self.niche_weights['crossover_potential']
            )
            
            # Determine compatibility type
            compatibility_type = self._determine_compatibility_type(
                overall_compatibility, niche_overlap, crossover_potential
            )
            
            # Generate collaboration opportunities
            opportunities = await self._generate_collaboration_opportunities(
                profile_a, profile_b, compatibility_type
            )
            
            # Assess risk factors
            risk_factors = await self._assess_risk_factors(profile_a, profile_b)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(
                overall_compatibility, compatibility_type, risk_factors
            )
            
            # Generate project recommendations
            project_types = await self._recommend_project_types(profile_a, profile_b)
            
            # Calculate niche-specific scores
            niche_scores = await self._calculate_niche_specific_scores(profile_a, profile_b)
            
            # Generate detailed analysis
            detailed_analysis = await self._generate_detailed_analysis(
                profile_a, profile_b, niche_overlap, audience_alignment,
                content_synergy, crossover_potential
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                profile_a, profile_b, overall_compatibility
            )
            
            result = NicheCompatibilityResult(
                creator_a_id=profile_a.creator_id,
                creator_b_id=profile_b.creator_id,
                overall_compatibility=overall_compatibility,
                compatibility_type=compatibility_type,
                niche_overlap_score=niche_overlap,
                audience_alignment_score=audience_alignment,
                content_synergy_score=content_synergy,
                crossover_potential=crossover_potential,
                collaboration_opportunities=opportunities,
                risk_factors=risk_factors,
                success_probability=success_probability,
                recommended_project_types=project_types,
                niche_specific_scores=niche_scores,
                detailed_analysis=detailed_analysis,
                confidence_score=confidence_score
            )
            
            logger.info(f"✅ Niche compatibility analysis completed: {overall_compatibility:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in niche compatibility analysis: {e}")
            raise
    
    async def _calculate_niche_overlap(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate niche overlap score between two creators"""
        try:
            # Primary niche overlap
            primary_a = set(profile_a.primary_niches)
            primary_b = set(profile_b.primary_niches)
            primary_overlap = len(primary_a.intersection(primary_b)) / max(len(primary_a.union(primary_b)), 1)
            
            # Secondary niche overlap
            secondary_a = set(profile_a.secondary_niches)
            secondary_b = set(profile_b.secondary_niches)
            secondary_overlap = len(secondary_a.intersection(secondary_b)) / max(len(secondary_a.union(secondary_b)), 1)
            
            # Authority-weighted overlap
            authority_overlap = 0.0
            common_niches = primary_a.intersection(primary_b).union(secondary_a.intersection(secondary_b))
            
            for niche in common_niches:
                auth_a = profile_a.niche_authority.get(niche, 0)
                auth_b = profile_b.niche_authority.get(niche, 0)
                authority_overlap += min(auth_a, auth_b)
            
            # Weighted combination
            overlap_score = (
                primary_overlap * 0.6 +
                secondary_overlap * 0.3 +
                (authority_overlap / max(len(common_niches), 1)) * 0.1
            )
            
            return min(overlap_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating niche overlap: {e}")
            return 0.0
    
    async def _calculate_audience_alignment(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate audience alignment score"""
        try:
            # Audience segment overlap
            segments_a = set(profile_a.audience_segments.keys())
            segments_b = set(profile_b.audience_segments.keys())
            common_segments = segments_a.intersection(segments_b)
            
            if not common_segments:
                return 0.0
            
            # Calculate weighted overlap
            overlap_sum = 0.0
            total_weight = 0.0
            
            for segment in common_segments:
                weight_a = profile_a.audience_segments[segment]
                weight_b = profile_b.audience_segments[segment]
                overlap_sum += min(weight_a, weight_b)
                total_weight += max(weight_a, weight_b)
            
            alignment_score = overlap_sum / max(total_weight, 0.1)
            return min(alignment_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating audience alignment: {e}")
            return 0.0
    
    async def _calculate_content_synergy(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate content synergy potential"""
        try:
            # Content style similarity
            style_similarity = 0.0
            common_styles = set(profile_a.content_style.keys()).intersection(
                set(profile_b.content_style.keys())
            )
            
            for style in common_styles:
                val_a = profile_a.content_style[style]
                val_b = profile_b.content_style[style]
                style_similarity += 1 - abs(val_a - val_b)
            
            if common_styles:
                style_similarity /= len(common_styles)
            
            # Content tag similarity
            if profile_a.content_tags and profile_b.content_tags:
                # Use cosine similarity on content tags
                vectorizer = TfidfVectorizer()
                tag_texts = [' '.join(profile_a.content_tags), ' '.join(profile_b.content_tags)]
                tag_vectors = vectorizer.fit_transform(tag_texts)
                tag_similarity = cosine_similarity(tag_vectors[0], tag_vectors[1])[0][0]
            else:
                tag_similarity = 0.0
            
            # Specialization complementarity
            spec_a = set(profile_a.specializations)
            spec_b = set(profile_b.specializations)
            spec_overlap = len(spec_a.intersection(spec_b))
            spec_complement = len(spec_a.union(spec_b)) - spec_overlap
            complementarity_score = spec_complement / max(len(spec_a.union(spec_b)), 1)
            
            # Combined synergy score
            synergy_score = (
                style_similarity * 0.4 +
                tag_similarity * 0.4 +
                complementarity_score * 0.2
            )
            
            return min(synergy_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content synergy: {e}")
            return 0.0
    
    async def _calculate_crossover_potential(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate crossover potential between different niches"""
        try:
            # Cross-niche experience
            crossover_exp = 0.0
            for (niche_1, niche_2), experience in profile_a.cross_niche_experience.items():
                if niche_1 in profile_b.primary_niches or niche_2 in profile_b.primary_niches:
                    crossover_exp += experience
            
            for (niche_1, niche_2), experience in profile_b.cross_niche_experience.items():
                if niche_1 in profile_a.primary_niches or niche_2 in profile_a.primary_niches:
                    crossover_exp += experience
            
            # Niche adjacency (how well niches work together)
            adjacency_score = await self._calculate_niche_adjacency(profile_a, profile_b)
            
            # Market opportunity for crossover
            market_score = await self._calculate_crossover_market_opportunity(profile_a, profile_b)
            
            crossover_potential = (
                (crossover_exp / 2.0) * 0.4 +
                adjacency_score * 0.4 +
                market_score * 0.2
            )
            
            return min(crossover_potential, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating crossover potential: {e}")
            return 0.0
    
    async def _calculate_niche_adjacency(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate how adjacent/compatible different niches are"""
        # Predefined adjacency matrix for different niche combinations
        adjacency_matrix = {
            (NicheCategory.MUSIC, NicheCategory.VIDEO): 0.9,
            (NicheCategory.GAMING, NicheCategory.TECHNOLOGY): 0.8,
            (NicheCategory.FITNESS, NicheCategory.LIFESTYLE): 0.8,
            (NicheCategory.FASHION, NicheCategory.LIFESTYLE): 0.9,
            (NicheCategory.FOOD, NicheCategory.TRAVEL): 0.7,
            (NicheCategory.EDUCATION, NicheCategory.SCIENCE): 0.8,
            (NicheCategory.BUSINESS, NicheCategory.TECHNOLOGY): 0.7,
            (NicheCategory.ART, NicheCategory.FASHION): 0.6,
            # Add more combinations as needed
        }
        
        max_adjacency = 0.0
        
        for niche_a in profile_a.primary_niches:
            for niche_b in profile_b.primary_niches:
                if niche_a != niche_b:
                    # Check both directions
                    adj_score = adjacency_matrix.get((niche_a, niche_b), 0.0)
                    adj_score = max(adj_score, adjacency_matrix.get((niche_b, niche_a), 0.0))
                    max_adjacency = max(max_adjacency, adj_score)
        
        return max_adjacency
    
    async def _calculate_crossover_market_opportunity(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> float:
        """Calculate market opportunity for niche crossover"""
        # Simplified market opportunity calculation
        # In real implementation, this would use market data
        
        niche_combinations = []
        for niche_a in profile_a.primary_niches:
            for niche_b in profile_b.primary_niches:
                if niche_a != niche_b:
                    niche_combinations.append((niche_a, niche_b))
        
        if not niche_combinations:
            return 0.0
        
        # Mock market opportunity scores (replace with real market data)
        market_opportunities = {
            (NicheCategory.MUSIC, NicheCategory.GAMING): 0.8,
            (NicheCategory.FITNESS, NicheCategory.TECHNOLOGY): 0.7,
            (NicheCategory.EDUCATION, NicheCategory.ENTERTAINMENT): 0.9,
            # Add more based on market research
        }
        
        max_opportunity = 0.0
        for combo in niche_combinations:
            opportunity = market_opportunities.get(combo, 0.5)  # Default moderate opportunity
            max_opportunity = max(max_opportunity, opportunity)
        
        return max_opportunity
    
    def _determine_compatibility_type(
        self,
        overall_compatibility: float,
        niche_overlap: float,
        crossover_potential: float
    ) -> CompatibilityType:
        """Determine the type of compatibility"""
        if overall_compatibility >= 0.9 and niche_overlap >= 0.8:
            return CompatibilityType.PERFECT_MATCH
        elif overall_compatibility >= 0.7 and crossover_potential >= 0.6:
            return CompatibilityType.COMPLEMENTARY
        elif niche_overlap >= 0.5 and overall_compatibility >= 0.6:
            return CompatibilityType.ADJACENT
        elif crossover_potential >= 0.7:
            return CompatibilityType.CROSSOVER
        elif overall_compatibility >= 0.4:
            return CompatibilityType.EXPERIMENTAL
        else:
            return CompatibilityType.INCOMPATIBLE
    
    async def _generate_collaboration_opportunities(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile,
        compatibility_type: CompatibilityType
    ) -> List[Dict[str, Any]]:
        """Generate specific collaboration opportunities"""
        opportunities = []
        
        # Based on compatibility type, suggest different opportunities
        if compatibility_type == CompatibilityType.PERFECT_MATCH:
            opportunities.extend([
                {
                    "type": "joint_content_series",
                    "description": "Create a collaborative content series leveraging both creators' strengths",
                    "potential_impact": "high",
                    "estimated_engagement_boost": 1.5
                },
                {
                    "type": "cross_promotion",
                    "description": "Mutual audience introduction and cross-promotion",
                    "potential_impact": "high",
                    "estimated_engagement_boost": 1.3
                }
            ])
        
        elif compatibility_type == CompatibilityType.COMPLEMENTARY:
            opportunities.extend([
                {
                    "type": "skill_exchange",
                    "description": "Exchange expertise in different areas",
                    "potential_impact": "medium",
                    "estimated_engagement_boost": 1.2
                },
                {
                    "type": "format_fusion",
                    "description": "Combine different content formats for unique experiences",
                    "potential_impact": "high",
                    "estimated_engagement_boost": 1.4
                }
            ])
        
        elif compatibility_type == CompatibilityType.CROSSOVER:
            opportunities.extend([
                {
                    "type": "niche_bridge",
                    "description": "Create content that bridges different niches",
                    "potential_impact": "medium",
                    "estimated_engagement_boost": 1.3
                },
                {
                    "type": "audience_expansion",
                    "description": "Help each other expand into new audience segments",
                    "potential_impact": "high",
                    "estimated_engagement_boost": 1.6
                }
            ])
        
        return opportunities
    
    async def _assess_risk_factors(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> List[str]:
        """Assess potential risk factors for collaboration"""
        risks = []
        
        # Authority imbalance
        avg_auth_a = np.mean(list(profile_a.niche_authority.values())) if profile_a.niche_authority else 0
        avg_auth_b = np.mean(list(profile_b.niche_authority.values())) if profile_b.niche_authority else 0
        
        if abs(avg_auth_a - avg_auth_b) > 0.5:
            risks.append("authority_imbalance")
        
        # Audience mismatch
        common_segments = set(profile_a.audience_segments.keys()).intersection(
            set(profile_b.audience_segments.keys())
        )
        if len(common_segments) < 2:
            risks.append("limited_audience_overlap")
        
        # Content style conflict
        style_conflicts = 0
        for style in set(profile_a.content_style.keys()).intersection(set(profile_b.content_style.keys())):
            if abs(profile_a.content_style[style] - profile_b.content_style[style]) > 0.7:
                style_conflicts += 1
        
        if style_conflicts > len(profile_a.content_style) * 0.5:
            risks.append("content_style_mismatch")
        
        return risks
    
    def _calculate_success_probability(
        self,
        overall_compatibility: float,
        compatibility_type: CompatibilityType,
        risk_factors: List[str]
    ) -> float:
        """Calculate probability of collaboration success"""
        base_probability = overall_compatibility
        
        # Type-based adjustments
        type_multipliers = {
            CompatibilityType.PERFECT_MATCH: 1.2,
            CompatibilityType.COMPLEMENTARY: 1.1,
            CompatibilityType.ADJACENT: 1.0,
            CompatibilityType.CROSSOVER: 0.9,
            CompatibilityType.EXPERIMENTAL: 0.7,
            CompatibilityType.INCOMPATIBLE: 0.3
        }
        
        probability = base_probability * type_multipliers.get(compatibility_type, 1.0)
        
        # Risk factor penalties
        risk_penalty = len(risk_factors) * 0.1
        probability = max(0.0, probability - risk_penalty)
        
        return min(probability, 1.0)
    
    async def _recommend_project_types(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> List[str]:
        """Recommend specific project types for collaboration"""
        projects = []
        
        # Based on niche combinations
        combined_niches = set(profile_a.primary_niches).union(set(profile_b.primary_niches))
        
        if NicheCategory.MUSIC in combined_niches and NicheCategory.VIDEO in combined_niches:
            projects.extend(["music_video", "concert_documentary", "behind_scenes_series"])
        
        if NicheCategory.GAMING in combined_niches and NicheCategory.TECHNOLOGY in combined_niches:
            projects.extend(["tech_review_gaming", "game_development_series", "esports_analysis"])
        
        if NicheCategory.FITNESS in combined_niches and NicheCategory.LIFESTYLE in combined_niches:
            projects.extend(["wellness_challenge", "lifestyle_transformation", "healthy_cooking_series"])
        
        # Add general project types
        projects.extend(["collaborative_podcast", "joint_live_stream", "educational_workshop"])
        
        return projects
    
    async def _calculate_niche_specific_scores(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile
    ) -> Dict[NicheCategory, float]:
        """Calculate compatibility scores for specific niches"""
        scores = {}
        
        all_niches = set(profile_a.primary_niches + profile_a.secondary_niches +
                        profile_b.primary_niches + profile_b.secondary_niches)
        
        for niche in all_niches:
            auth_a = profile_a.niche_authority.get(niche, 0)
            auth_b = profile_b.niche_authority.get(niche, 0)
            
            if auth_a > 0 and auth_b > 0:
                # Both have experience in this niche
                scores[niche] = min(auth_a, auth_b) + 0.2 * max(auth_a, auth_b)
            elif auth_a > 0 or auth_b > 0:
                # One has experience, potential for knowledge transfer
                scores[niche] = max(auth_a, auth_b) * 0.6
            else:
                scores[niche] = 0.0
        
        return scores
    
    async def _generate_detailed_analysis(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile,
        niche_overlap: float,
        audience_alignment: float,
        content_synergy: float,
        crossover_potential: float
    ) -> Dict[str, Any]:
        """Generate detailed compatibility analysis"""
        return {
            "niche_analysis": {
                "primary_overlap": len(set(profile_a.primary_niches).intersection(set(profile_b.primary_niches))),
                "secondary_overlap": len(set(profile_a.secondary_niches).intersection(set(profile_b.secondary_niches))),
                "unique_niches_a": list(set(profile_a.primary_niches) - set(profile_b.primary_niches)),
                "unique_niches_b": list(set(profile_b.primary_niches) - set(profile_a.primary_niches))
            },
            "audience_analysis": {
                "shared_segments": list(set(profile_a.audience_segments.keys()).intersection(
                    set(profile_b.audience_segments.keys())
                )),
                "audience_size_ratio": len(profile_a.audience_segments) / max(len(profile_b.audience_segments), 1)
            },
            "content_analysis": {
                "tag_overlap": len(set(profile_a.content_tags).intersection(set(profile_b.content_tags))),
                "specialization_complement": list(set(profile_a.specializations).symmetric_difference(
                    set(profile_b.specializations)
                ))
            },
            "compatibility_breakdown": {
                "niche_overlap": niche_overlap,
                "audience_alignment": audience_alignment,
                "content_synergy": content_synergy,
                "crossover_potential": crossover_potential
            }
        }
    
    def _calculate_confidence_score(
        self,
        profile_a: NicheProfile,
        profile_b: NicheProfile,
        overall_compatibility: float
    ) -> float:
        """Calculate confidence in the compatibility analysis"""
        # Factors affecting confidence
        data_completeness_a = self._calculate_profile_completeness(profile_a)
        data_completeness_b = self._calculate_profile_completeness(profile_b)
        
        # Average data completeness
        avg_completeness = (data_completeness_a + data_completeness_b) / 2
        
        # Confidence based on compatibility score and data quality
        confidence = (overall_compatibility * 0.6) + (avg_completeness * 0.4)
        
        return min(confidence, 1.0)
    
    def _calculate_profile_completeness(self, profile: NicheProfile) -> float:
        """Calculate how complete a niche profile is"""
        completeness_factors = {
            'has_primary_niches': len(profile.primary_niches) > 0,
            'has_secondary_niches': len(profile.secondary_niches) > 0,
            'has_content_tags': len(profile.content_tags) > 0,
            'has_audience_segments': len(profile.audience_segments) > 0,
            'has_specializations': len(profile.specializations) > 0,
            'has_content_style': len(profile.content_style) > 0,
            'has_niche_authority': len(profile.niche_authority) > 0,
            'has_cross_niche_experience': len(profile.cross_niche_experience) > 0
        }
        
        completed_factors = sum(completeness_factors.values())
        total_factors = len(completeness_factors)
        
        return completed_factors / total_factors
    
    async def generate_niche_insights(self, profile: NicheProfile) -> NicheInsights:
        """Generate insights and recommendations for niche optimization"""
        try:
            logger.info(f"🔍 Generating niche insights for creator: {profile.creator_id}")
            
            # Analyze current niche strength
            current_strength = {}
            for niche in NicheCategory:
                authority = profile.niche_authority.get(niche, 0)
                engagement = profile.engagement_by_niche.get(niche, {})
                avg_engagement = np.mean(list(engagement.values())) if engagement else 0
                current_strength[niche] = (authority * 0.7) + (avg_engagement * 0.3)
            
            # Identify growth opportunities
            growth_opportunities = await self._identify_growth_opportunities(profile)
            
            # Detect market gaps
            market_gaps = await self._detect_market_gaps(profile)
            
            # Get trending niches (mock data - replace with real trend analysis)
            trending_niches = [NicheCategory.TECHNOLOGY, NicheCategory.EDUCATION, NicheCategory.FITNESS]
            
            # Find optimal collaboration targets
            optimal_collaborations = await self._find_optimal_collaboration_targets(profile)
            
            # Generate expansion recommendations
            expansion_recommendations = await self._generate_expansion_recommendations(profile)
            
            # Create audience development strategies
            audience_strategies = await self._create_audience_development_strategies(profile)
            
            # Perform content gap analysis
            content_gap_analysis = await self._perform_content_gap_analysis(profile)
            
            # Competitive analysis
            competitive_analysis = await self._perform_competitive_analysis(profile)
            
            insights = NicheInsights(
                creator_id=profile.creator_id,
                current_niche_strength=current_strength,
                growth_opportunities=growth_opportunities,
                market_gaps=market_gaps,
                trending_niches=trending_niches,
                optimal_collaborations=optimal_collaborations,
                niche_expansion_recommendations=expansion_recommendations,
                audience_development_strategies=audience_strategies,
                content_gap_analysis=content_gap_analysis,
                competitive_analysis=competitive_analysis
            )
            
            logger.info(f"✅ Niche insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating niche insights: {e}")
            raise
    
    async def _identify_growth_opportunities(self, profile: NicheProfile) -> List[Dict[str, Any]]:
        """Identify growth opportunities for the creator"""
        opportunities = []
        
        # Look for niches with medium authority that could be grown
        for niche, authority in profile.niche_authority.items():
            if 0.3 <= authority <= 0.7:
                opportunities.append({
                    "type": "niche_strengthening",
                    "niche": niche.value,
                    "current_authority": authority,
                    "growth_potential": 1.0 - authority,
                    "recommendation": f"Focus on building authority in {niche.value}"
                })
        
        # Look for trending niches that align with current strengths
        for niche in [NicheCategory.TECHNOLOGY, NicheCategory.EDUCATION]:
            if niche not in profile.niche_authority or profile.niche_authority[niche] < 0.3:
                opportunities.append({
                    "type": "trend_alignment",
                    "niche": niche.value,
                    "trend_strength": 0.8,
                    "alignment_score": self._calculate_trend_alignment(profile, niche),
                    "recommendation": f"Explore opportunities in trending {niche.value} niche"
                })
        
        return opportunities
    
    def _calculate_trend_alignment(self, profile: NicheProfile, trend_niche: NicheCategory) -> float:
        """Calculate how well a creator aligns with a trending niche"""
        # Simplified alignment calculation
        # In real implementation, this would consider content tags, audience, etc.
        
        if trend_niche in profile.secondary_niches:
            return 0.7
        elif any(tag in ['tech', 'education', 'learning'] for tag in profile.content_tags):
            return 0.5
        else:
            return 0.3
    
    async def _detect_market_gaps(self, profile: NicheProfile) -> List[str]:
        """Detect market gaps that the creator could fill"""
        # Mock gap detection - replace with real market analysis
        gaps = []
        
        if NicheCategory.EDUCATION in profile.primary_niches:
            gaps.append("Interactive learning experiences for professionals")
        
        if NicheCategory.TECHNOLOGY in profile.primary_niches:
            gaps.append("Tech tutorials for non-technical audiences")
        
        if NicheCategory.FITNESS in profile.primary_niches:
            gaps.append("Accessible fitness content for people with disabilities")
        
        return gaps
    
    async def _find_optimal_collaboration_targets(self, profile: NicheProfile) -> List[str]:
        """Find optimal collaboration target types"""
        targets = []
        
        for niche in profile.primary_niches:
            if niche == NicheCategory.MUSIC:
                targets.extend(["video creators", "dancers", "sound engineers"])
            elif niche == NicheCategory.TECHNOLOGY:
                targets.extend(["educators", "business creators", "designers"])
            elif niche == NicheCategory.FITNESS:
                targets.extend(["nutritionists", "lifestyle bloggers", "mental health advocates"])
        
        return list(set(targets))  # Remove duplicates
    
    async def _generate_expansion_recommendations(self, profile: NicheProfile) -> List[Dict[str, Any]]:
        """Generate niche expansion recommendations"""
        recommendations = []
        
        # Adjacent niche expansion
        for primary_niche in profile.primary_niches:
            adjacent_niches = await self._get_adjacent_niches(primary_niche)
            for adjacent in adjacent_niches:
                if adjacent not in profile.primary_niches and adjacent not in profile.secondary_niches:
                    recommendations.append({
                        "type": "adjacent_expansion",
                        "target_niche": adjacent.value,
                        "synergy_potential": 0.7,
                        "entry_difficulty": "medium",
                        "recommendation": f"Expand into {adjacent.value} as it complements {primary_niche.value}"
                    })
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    async def _get_adjacent_niches(self, niche: NicheCategory) -> List[NicheCategory]:
        """Get niches adjacent to the given niche"""
        adjacency_map = {
            NicheCategory.MUSIC: [NicheCategory.VIDEO, NicheCategory.ART],
            NicheCategory.TECHNOLOGY: [NicheCategory.EDUCATION, NicheCategory.BUSINESS, NicheCategory.GAMING],
            NicheCategory.FITNESS: [NicheCategory.LIFESTYLE, NicheCategory.FOOD],
            NicheCategory.FASHION: [NicheCategory.LIFESTYLE, NicheCategory.ART],
            # Add more mappings as needed
        }
        
        return adjacency_map.get(niche, [])
    
    async def _create_audience_development_strategies(self, profile: NicheProfile) -> List[str]:
        """Create audience development strategies"""
        strategies = []
        
        # Based on current audience segments
        if 'young_adults' in profile.audience_segments:
            strategies.append("Leverage TikTok and Instagram Reels for viral content")
        
        if 'professionals' in profile.audience_segments:
            strategies.append("Create LinkedIn-focused professional development content")
        
        if 'hobbyists' in profile.audience_segments:
            strategies.append("Develop beginner-friendly tutorial series")
        
        # Generic strategies
        strategies.extend([
            "Cross-pollinate audiences through strategic collaborations",
            "Create content that bridges multiple interest areas",
            "Engage in community building through interactive content"
        ])
        
        return strategies
    
    async def _perform_content_gap_analysis(self, profile: NicheProfile) -> Dict[str, Any]:
        """Perform content gap analysis"""
        return {
            "underrepresented_formats": ["long-form video", "interactive content", "live streams"],
            "missing_topics": ["beginner guides", "advanced techniques", "industry insights"],
            "content_frequency_gaps": ["inconsistent posting in fitness niche", "low engagement in lifestyle content"],
            "quality_improvements": ["better audio quality", "improved visual design", "clearer explanations"]
        }
    
    async def _perform_competitive_analysis(self, profile: NicheProfile) -> Dict[str, Any]:
        """Perform competitive analysis"""
        return {
            "competitive_advantages": ["unique style", "strong community engagement", "consistent quality"],
            "areas_for_improvement": ["content variety", "posting frequency", "cross-platform presence"],
            "market_position": "mid-tier with growth potential",
            "differentiation_opportunities": ["niche expertise", "unique perspective", "personal branding"]
        }


# Export main classes and functions
__all__ = [
    'NicheCompatibilityEngine',
    'NicheProfile',
    'NicheCompatibilityResult',
    'NicheInsights',
    'NicheCategory',
    'CompatibilityType'
]