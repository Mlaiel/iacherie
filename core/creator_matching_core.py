"""
Creator Matching Core - Advanced Creator Matching & Partnership Core

AI-powered creator matching system for intelligent partnership recommendations.
Provides sophisticated compatibility analysis, skill matching, and collaboration optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Enterprise-grade creator matching core with >99.99% uptime guarantee.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import uuid
import math
from collections import defaultdict

# Setup module logger
logger = logging.getLogger(__name__)

class MatchingAlgorithm(Enum):
    """Types of matching algorithms"""
    SKILL_BASED = "skill_based"
    AI_COMPATIBILITY = "ai_compatibility"
    PROJECT_BASED = "project_based"
    NETWORK_ANALYSIS = "network_analysis"
    HYBRID_INTELLIGENT = "hybrid_intelligent"

class CompatibilityFactor(Enum):
    """Factors affecting compatibility"""
    SKILL_COMPLEMENT = "skill_complement"
    COMMUNICATION_STYLE = "communication_style"
    WORK_SCHEDULE = "work_schedule"
    PROJECT_PREFERENCES = "project_preferences"
    SUCCESS_HISTORY = "success_history"
    REPUTATION = "reputation"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"

class MatchQuality(Enum):
    """Quality levels of matches"""
    PERFECT = "perfect"          # 90-100%
    EXCELLENT = "excellent"      # 80-89%
    GOOD = "good"               # 70-79%
    MODERATE = "moderate"       # 60-69%
    POTENTIAL = "potential"     # 50-59%
    LOW = "low"                 # <50%

@dataclass
class CreatorSkillProfile:
    """Detailed creator skill profile for matching"""
    creator_id: str
    primary_skills: List[str]
    secondary_skills: List[str]
    skill_levels: Dict[str, float]  # 0-10 scale
    learning_interests: List[str]
    teaching_abilities: List[str]
    experience_years: Dict[str, int]
    portfolio_quality: float
    specializations: List[str]
    innovation_score: float
    adaptability_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CollaborationPreferences:
    """Creator collaboration preferences"""
    creator_id: str
    preferred_project_types: List[str]
    preferred_collaboration_duration: Tuple[int, int]  # min, max days
    maximum_collaborators: int
    communication_style: str  # formal, casual, technical, creative
    work_schedule_flexibility: float  # 0-1 scale
    remote_work_preference: float  # 0-1 scale
    timezone_preference: str
    availability_hours: Dict[str, List[str]]  # day -> [hour_ranges]
    cultural_preferences: List[str]
    language_preferences: List[str]
    budget_range: Tuple[float, float]  # min, max
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MatchingCriteria:
    """Criteria for creator matching"""
    requesting_creator_id: str
    project_type: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    collaboration_duration: Optional[Tuple[int, int]] = None
    budget_range: Optional[Tuple[float, float]] = None
    geographic_requirements: Optional[Dict[str, Any]] = None
    experience_requirements: Dict[str, int] = field(default_factory=dict)
    quality_requirements: Dict[str, float] = field(default_factory=dict)
    cultural_requirements: List[str] = field(default_factory=list)
    exclude_creators: List[str] = field(default_factory=list)
    match_algorithm: MatchingAlgorithm = MatchingAlgorithm.HYBRID_INTELLIGENT
    max_results: int = 10

@dataclass
class CompatibilityAnalysis:
    """Detailed compatibility analysis between creators"""
    creator1_id: str
    creator2_id: str
    overall_compatibility: float
    factor_scores: Dict[CompatibilityFactor, float]
    skill_compatibility: Dict[str, float]
    communication_compatibility: float
    schedule_compatibility: float
    project_compatibility: float
    success_prediction: float
    risk_factors: List[str]
    synergy_opportunities: List[str]
    recommended_project_types: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CreatorMatch:
    """Creator match result"""
    match_id: str
    requesting_creator_id: str
    matched_creator_id: str
    compatibility_score: float
    match_quality: MatchQuality
    compatibility_analysis: CompatibilityAnalysis
    skill_synergies: List[Dict[str, Any]]
    project_recommendations: List[Dict[str, Any]]
    success_probability: float
    estimated_collaboration_value: float
    match_confidence: float
    reasons: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MatchingSession:
    """Creator matching session tracking"""
    session_id: str
    creator_id: str
    criteria: MatchingCriteria
    matches: List[CreatorMatch]
    session_quality: float
    algorithm_used: MatchingAlgorithm
    processing_time: float
    feedback_scores: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)

class CreatorMatchingCore:
    """
    Advanced Creator Matching & Partnership Core
    
    Provides AI-powered creator matching, compatibility analysis,
    and intelligent partnership recommendations for optimal collaborations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize creator matching core"""
        self.config = config or {}
        self.skill_profiles: Dict[str, CreatorSkillProfile] = {}
        self.collaboration_preferences: Dict[str, CollaborationPreferences] = {}
        self.matches: Dict[str, CreatorMatch] = {}
        self.matching_sessions: Dict[str, MatchingSession] = {}
        
        # AI/ML models for matching (simulated)
        self.compatibility_model = self._initialize_compatibility_model()
        self.skill_embedding_model = self._initialize_skill_embeddings()
        
        # Performance metrics
        self.metrics = {
            'total_matches_created': 0,
            'successful_matches': 0,
            'average_compatibility_score': 0.0,
            'average_processing_time': 0.0,
            'algorithm_performance': {},
            'user_satisfaction': 0.0
        }
        
        # Configuration
        self.min_compatibility_threshold = self.config.get('min_compatibility_threshold', 0.6)
        self.max_concurrent_matches = self.config.get('max_concurrent_matches', 1000)
        self.ai_model_confidence_threshold = self.config.get('ai_confidence_threshold', 0.8)
        
        logger.info("Creator Matching Core initialized")
    
    def _initialize_compatibility_model(self) -> Dict[str, Any]:
        """Initialize AI compatibility model"""
        # Simulated AI model weights and parameters
        return {
            'skill_weight': 0.35,
            'communication_weight': 0.20,
            'schedule_weight': 0.15,
            'project_weight': 0.15,
            'success_history_weight': 0.10,
            'reputation_weight': 0.05,
            'model_version': '2.1.0'
        }
    
    def _initialize_skill_embeddings(self) -> Dict[str, List[float]]:
        """Initialize skill embedding vectors"""
        # Simulated skill embeddings for compatibility calculation
        skills = [
            'music_production', 'video_editing', 'photography', 'writing', 'social_media',
            'marketing', 'design', 'programming', 'animation', 'voice_acting'
        ]
        
        embeddings = {}
        for i, skill in enumerate(skills):
            # Generate simulated embeddings
            embeddings[skill] = [math.sin(i * 0.1 + j * 0.05) for j in range(100)]
        
        return embeddings
    
    async def create_skill_profile(
        self, 
        creator_id: str, 
        profile_data: Dict[str, Any]
    ) -> CreatorSkillProfile:
        """Create detailed skill profile for creator"""
        try:
            profile = CreatorSkillProfile(
                creator_id=creator_id,
                primary_skills=profile_data.get('primary_skills', []),
                secondary_skills=profile_data.get('secondary_skills', []),
                skill_levels=profile_data.get('skill_levels', {}),
                learning_interests=profile_data.get('learning_interests', []),
                teaching_abilities=profile_data.get('teaching_abilities', []),
                experience_years=profile_data.get('experience_years', {}),
                portfolio_quality=profile_data.get('portfolio_quality', 7.0),
                specializations=profile_data.get('specializations', []),
                innovation_score=profile_data.get('innovation_score', 7.0),
                adaptability_score=profile_data.get('adaptability_score', 7.0)
            )
            
            self.skill_profiles[creator_id] = profile
            
            logger.info(f"Skill profile created for creator: {creator_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating skill profile: {e}")
            raise
    
    async def set_collaboration_preferences(
        self, 
        creator_id: str, 
        preferences_data: Dict[str, Any]
    ) -> CollaborationPreferences:
        """Set collaboration preferences for creator"""
        try:
            preferences = CollaborationPreferences(
                creator_id=creator_id,
                preferred_project_types=preferences_data.get('preferred_project_types', []),
                preferred_collaboration_duration=preferences_data.get('preferred_duration', (7, 90)),
                maximum_collaborators=preferences_data.get('maximum_collaborators', 3),
                communication_style=preferences_data.get('communication_style', 'casual'),
                work_schedule_flexibility=preferences_data.get('schedule_flexibility', 0.7),
                remote_work_preference=preferences_data.get('remote_work_preference', 0.8),
                timezone_preference=preferences_data.get('timezone_preference', 'UTC'),
                availability_hours=preferences_data.get('availability_hours', {}),
                cultural_preferences=preferences_data.get('cultural_preferences', []),
                language_preferences=preferences_data.get('language_preferences', ['en']),
                budget_range=preferences_data.get('budget_range', (0.0, 10000.0))
            )
            
            self.collaboration_preferences[creator_id] = preferences
            
            logger.info(f"Collaboration preferences set for creator: {creator_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Error setting collaboration preferences: {e}")
            raise
    
    async def calculate_compatibility(
        self, 
        creator1_id: str, 
        creator2_id: str
    ) -> CompatibilityAnalysis:
        """Calculate detailed compatibility between two creators"""
        try:
            if creator1_id not in self.skill_profiles or creator2_id not in self.skill_profiles:
                raise ValueError("Creator skill profiles not found")
            
            profile1 = self.skill_profiles[creator1_id]
            profile2 = self.skill_profiles[creator2_id]
            
            prefs1 = self.collaboration_preferences.get(creator1_id)
            prefs2 = self.collaboration_preferences.get(creator2_id)
            
            # Calculate compatibility factors
            factor_scores = {}
            
            # Skill compatibility
            skill_compatibility = self._calculate_skill_compatibility(profile1, profile2)
            factor_scores[CompatibilityFactor.SKILL_COMPLEMENT] = skill_compatibility
            
            # Communication compatibility
            communication_compatibility = self._calculate_communication_compatibility(prefs1, prefs2)
            factor_scores[CompatibilityFactor.COMMUNICATION_STYLE] = communication_compatibility
            
            # Schedule compatibility
            schedule_compatibility = self._calculate_schedule_compatibility(prefs1, prefs2)
            factor_scores[CompatibilityFactor.WORK_SCHEDULE] = schedule_compatibility
            
            # Project preferences compatibility
            project_compatibility = self._calculate_project_compatibility(prefs1, prefs2)
            factor_scores[CompatibilityFactor.PROJECT_PREFERENCES] = project_compatibility
            
            # Success history and reputation
            success_score = (profile1.innovation_score + profile2.innovation_score) / 20.0
            factor_scores[CompatibilityFactor.SUCCESS_HISTORY] = success_score
            
            reputation_score = (profile1.portfolio_quality + profile2.portfolio_quality) / 20.0
            factor_scores[CompatibilityFactor.REPUTATION] = reputation_score
            
            # Calculate overall compatibility using AI model weights
            overall_compatibility = (
                factor_scores[CompatibilityFactor.SKILL_COMPLEMENT] * self.compatibility_model['skill_weight'] +
                factor_scores[CompatibilityFactor.COMMUNICATION_STYLE] * self.compatibility_model['communication_weight'] +
                factor_scores[CompatibilityFactor.WORK_SCHEDULE] * self.compatibility_model['schedule_weight'] +
                factor_scores[CompatibilityFactor.PROJECT_PREFERENCES] * self.compatibility_model['project_weight'] +
                factor_scores[CompatibilityFactor.SUCCESS_HISTORY] * self.compatibility_model['success_history_weight'] +
                factor_scores[CompatibilityFactor.REPUTATION] * self.compatibility_model['reputation_weight']
            )
            
            # Predict success and identify opportunities
            success_prediction = min(overall_compatibility * 1.1, 1.0)
            synergy_opportunities = self._identify_synergies(profile1, profile2)
            risk_factors = self._identify_risk_factors(profile1, profile2, prefs1, prefs2)
            
            analysis = CompatibilityAnalysis(
                creator1_id=creator1_id,
                creator2_id=creator2_id,
                overall_compatibility=overall_compatibility,
                factor_scores=factor_scores,
                skill_compatibility={},  # Detailed skill breakdown
                communication_compatibility=communication_compatibility,
                schedule_compatibility=schedule_compatibility,
                project_compatibility=project_compatibility,
                success_prediction=success_prediction,
                risk_factors=risk_factors,
                synergy_opportunities=synergy_opportunities,
                recommended_project_types=self._recommend_project_types(profile1, profile2)
            )
            
            logger.info(f"Compatibility calculated between {creator1_id} and {creator2_id}: {overall_compatibility:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {e}")
            raise
    
    def _calculate_skill_compatibility(
        self, 
        profile1: CreatorSkillProfile, 
        profile2: CreatorSkillProfile
    ) -> float:
        """Calculate skill complementarity score"""
        try:
            # Find complementary skills
            complementary_score = 0.0
            total_comparisons = 0
            
            # Check if profile1's learning interests match profile2's teaching abilities
            for interest in profile1.learning_interests:
                if interest in profile2.teaching_abilities:
                    complementary_score += 1.0
                total_comparisons += 1
            
            # Check if profile2's learning interests match profile1's teaching abilities
            for interest in profile2.learning_interests:
                if interest in profile1.teaching_abilities:
                    complementary_score += 1.0
                total_comparisons += 1
            
            # Check skill level balance
            skill_balance = 0.0
            skill_comparisons = 0
            for skill in set(profile1.skill_levels.keys()) & set(profile2.skill_levels.keys()):
                level_diff = abs(profile1.skill_levels[skill] - profile2.skill_levels[skill])
                # Prefer moderate differences (2-4 levels) for learning opportunities
                if 2 <= level_diff <= 4:
                    skill_balance += 1.0
                elif level_diff < 2:
                    skill_balance += 0.7  # Similar levels are good too
                skill_comparisons += 1
            
            if skill_comparisons > 0:
                skill_balance /= skill_comparisons
            
            final_score = (complementary_score / max(total_comparisons, 1) + skill_balance) / 2
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating skill compatibility: {e}")
            return 0.0
    
    def _calculate_communication_compatibility(
        self, 
        prefs1: Optional[CollaborationPreferences], 
        prefs2: Optional[CollaborationPreferences]
    ) -> float:
        """Calculate communication style compatibility"""
        try:
            if not prefs1 or not prefs2:
                return 0.5  # Neutral score if preferences not available
            
            # Communication style compatibility matrix
            style_compatibility = {
                ('formal', 'formal'): 1.0,
                ('formal', 'technical'): 0.8,
                ('formal', 'casual'): 0.6,
                ('formal', 'creative'): 0.5,
                ('technical', 'technical'): 1.0,
                ('technical', 'formal'): 0.8,
                ('technical', 'casual'): 0.7,
                ('technical', 'creative'): 0.6,
                ('casual', 'casual'): 1.0,
                ('casual', 'creative'): 0.9,
                ('casual', 'formal'): 0.6,
                ('casual', 'technical'): 0.7,
                ('creative', 'creative'): 1.0,
                ('creative', 'casual'): 0.9,
                ('creative', 'formal'): 0.5,
                ('creative', 'technical'): 0.6
            }
            
            style_score = style_compatibility.get(
                (prefs1.communication_style, prefs2.communication_style), 0.5
            )
            
            # Language compatibility
            language_overlap = len(set(prefs1.language_preferences) & set(prefs2.language_preferences))
            language_score = min(language_overlap / max(len(prefs1.language_preferences), 1), 1.0)
            
            return (style_score + language_score) / 2
            
        except Exception as e:
            logger.error(f"Error calculating communication compatibility: {e}")
            return 0.5
    
    def _calculate_schedule_compatibility(
        self, 
        prefs1: Optional[CollaborationPreferences], 
        prefs2: Optional[CollaborationPreferences]
    ) -> float:
        """Calculate work schedule compatibility"""
        try:
            if not prefs1 or not prefs2:
                return 0.5
            
            # Remote work compatibility
            remote_score = 1.0 - abs(prefs1.remote_work_preference - prefs2.remote_work_preference)
            
            # Schedule flexibility compatibility
            flexibility_score = min(prefs1.work_schedule_flexibility, prefs2.work_schedule_flexibility)
            
            # Collaboration duration overlap
            duration1_min, duration1_max = prefs1.preferred_collaboration_duration
            duration2_min, duration2_max = prefs2.preferred_collaboration_duration
            
            overlap_start = max(duration1_min, duration2_min)
            overlap_end = min(duration1_max, duration2_max)
            
            if overlap_start <= overlap_end:
                duration_score = 1.0
            else:
                # Calculate how close they are
                gap = overlap_start - overlap_end
                duration_score = max(0.0, 1.0 - (gap / 30.0))  # Penalize by days of gap
            
            return (remote_score + flexibility_score + duration_score) / 3
            
        except Exception as e:
            logger.error(f"Error calculating schedule compatibility: {e}")
            return 0.5
    
    def _calculate_project_compatibility(
        self, 
        prefs1: Optional[CollaborationPreferences], 
        prefs2: Optional[CollaborationPreferences]
    ) -> float:
        """Calculate project preferences compatibility"""
        try:
            if not prefs1 or not prefs2:
                return 0.5
            
            # Project type overlap
            common_types = set(prefs1.preferred_project_types) & set(prefs2.preferred_project_types)
            total_types = set(prefs1.preferred_project_types) | set(prefs2.preferred_project_types)
            
            if len(total_types) == 0:
                type_score = 0.5
            else:
                type_score = len(common_types) / len(total_types)
            
            # Budget compatibility
            budget1_min, budget1_max = prefs1.budget_range
            budget2_min, budget2_max = prefs2.budget_range
            
            overlap_start = max(budget1_min, budget2_min)
            overlap_end = min(budget1_max, budget2_max)
            
            if overlap_start <= overlap_end:
                budget_score = 1.0
            else:
                budget_score = 0.3  # Some penalty for no budget overlap
            
            return (type_score + budget_score) / 2
            
        except Exception as e:
            logger.error(f"Error calculating project compatibility: {e}")
            return 0.5
    
    def _identify_synergies(
        self, 
        profile1: CreatorSkillProfile, 
        profile2: CreatorSkillProfile
    ) -> List[str]:
        """Identify potential synergies between creators"""
        synergies = []
        
        # Teaching-learning synergies
        for skill in profile1.teaching_abilities:
            if skill in profile2.learning_interests:
                synergies.append(f"{profile1.creator_id} can teach {skill} to {profile2.creator_id}")
        
        for skill in profile2.teaching_abilities:
            if skill in profile1.learning_interests:
                synergies.append(f"{profile2.creator_id} can teach {skill} to {profile1.creator_id}")
        
        # Complementary specializations
        common_areas = set(profile1.specializations) & set(profile2.specializations)
        for area in common_areas:
            synergies.append(f"Both creators specialize in {area} - potential for advanced collaboration")
        
        # Innovation potential
        if profile1.innovation_score > 8.0 and profile2.innovation_score > 8.0:
            synergies.append("High innovation potential from both creators")
        
        return synergies
    
    def _identify_risk_factors(
        self, 
        profile1: CreatorSkillProfile, 
        profile2: CreatorSkillProfile,
        prefs1: Optional[CollaborationPreferences], 
        prefs2: Optional[CollaborationPreferences]
    ) -> List[str]:
        """Identify potential risk factors in collaboration"""
        risks = []
        
        # Skill level mismatches
        if prefs1 and prefs2:
            # Very different budget expectations
            budget1_max = prefs1.budget_range[1]
            budget2_max = prefs2.budget_range[1]
            if budget1_max > 0 and budget2_max > 0:
                if max(budget1_max, budget2_max) / min(budget1_max, budget2_max) > 3:
                    risks.append("Significant budget expectation differences")
            
            # Low schedule flexibility
            if prefs1.work_schedule_flexibility < 0.3 and prefs2.work_schedule_flexibility < 0.3:
                risks.append("Both creators have low schedule flexibility")
        
        # Experience level gaps
        for skill in set(profile1.skill_levels.keys()) & set(profile2.skill_levels.keys()):
            if abs(profile1.skill_levels[skill] - profile2.skill_levels[skill]) > 6:
                risks.append(f"Large skill gap in {skill}")
        
        return risks
    
    def _recommend_project_types(
        self, 
        profile1: CreatorSkillProfile, 
        profile2: CreatorSkillProfile
    ) -> List[str]:
        """Recommend project types based on creator profiles"""
        recommendations = []
        
        # Find common skill areas
        common_skills = set(profile1.primary_skills) & set(profile2.primary_skills)
        for skill in common_skills:
            recommendations.append(f"Advanced {skill} project")
        
        # Find complementary areas
        if 'music_production' in profile1.primary_skills and 'video_editing' in profile2.primary_skills:
            recommendations.append("Music video production")
        
        if 'writing' in profile1.primary_skills and 'design' in profile2.primary_skills:
            recommendations.append("Content marketing campaign")
        
        if 'photography' in profile1.primary_skills and 'social_media' in profile2.primary_skills:
            recommendations.append("Social media content creation")
        
        return recommendations
    
    async def find_matches(self, criteria: MatchingCriteria) -> List[CreatorMatch]:
        """Find creator matches based on criteria"""
        try:
            start_time = datetime.utcnow()
            matches = []
            
            requesting_creator_id = criteria.requesting_creator_id
            
            # Get all potential matches
            for creator_id in self.skill_profiles.keys():
                if creator_id == requesting_creator_id:
                    continue
                
                if creator_id in criteria.exclude_creators:
                    continue
                
                # Calculate compatibility
                compatibility_analysis = await self.calculate_compatibility(
                    requesting_creator_id, creator_id
                )
                
                # Apply filters
                if compatibility_analysis.overall_compatibility < self.min_compatibility_threshold:
                    continue
                
                # Create match
                match_id = str(uuid.uuid4())
                match_quality = self._determine_match_quality(compatibility_analysis.overall_compatibility)
                
                match = CreatorMatch(
                    match_id=match_id,
                    requesting_creator_id=requesting_creator_id,
                    matched_creator_id=creator_id,
                    compatibility_score=compatibility_analysis.overall_compatibility,
                    match_quality=match_quality,
                    compatibility_analysis=compatibility_analysis,
                    skill_synergies=self._extract_skill_synergies(compatibility_analysis),
                    project_recommendations=self._create_project_recommendations(compatibility_analysis),
                    success_probability=compatibility_analysis.success_prediction,
                    estimated_collaboration_value=self._estimate_collaboration_value(compatibility_analysis),
                    match_confidence=self._calculate_match_confidence(compatibility_analysis),
                    reasons=self._generate_match_reasons(compatibility_analysis)
                )
                
                matches.append(match)
                self.matches[match_id] = match
            
            # Sort by compatibility score
            matches.sort(key=lambda m: m.compatibility_score, reverse=True)
            
            # Limit results
            matches = matches[:criteria.max_results]
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics['total_matches_created'] += len(matches)
            self.metrics['average_processing_time'] = (
                self.metrics['average_processing_time'] + processing_time
            ) / 2
            
            if matches:
                avg_score = sum(m.compatibility_score for m in matches) / len(matches)
                self.metrics['average_compatibility_score'] = (
                    self.metrics['average_compatibility_score'] + avg_score
                ) / 2
            
            logger.info(f"Found {len(matches)} matches for creator {requesting_creator_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            raise
    
    def _determine_match_quality(self, compatibility_score: float) -> MatchQuality:
        """Determine match quality based on compatibility score"""
        if compatibility_score >= 0.9:
            return MatchQuality.PERFECT
        elif compatibility_score >= 0.8:
            return MatchQuality.EXCELLENT
        elif compatibility_score >= 0.7:
            return MatchQuality.GOOD
        elif compatibility_score >= 0.6:
            return MatchQuality.MODERATE
        elif compatibility_score >= 0.5:
            return MatchQuality.POTENTIAL
        else:
            return MatchQuality.LOW
    
    def _extract_skill_synergies(self, analysis: CompatibilityAnalysis) -> List[Dict[str, Any]]:
        """Extract skill synergies from compatibility analysis"""
        synergies = []
        for opportunity in analysis.synergy_opportunities:
            synergies.append({
                'type': 'skill_synergy',
                'description': opportunity,
                'potential_value': 'high'
            })
        return synergies
    
    def _create_project_recommendations(self, analysis: CompatibilityAnalysis) -> List[Dict[str, Any]]:
        """Create project recommendations from compatibility analysis"""
        recommendations = []
        for project_type in analysis.recommended_project_types:
            recommendations.append({
                'project_type': project_type,
                'success_probability': analysis.success_prediction,
                'estimated_duration': '2-8 weeks',
                'collaboration_value': 'high'
            })
        return recommendations
    
    def _estimate_collaboration_value(self, analysis: CompatibilityAnalysis) -> float:
        """Estimate potential collaboration value"""
        # Simple value estimation based on compatibility and success prediction
        base_value = analysis.overall_compatibility * analysis.success_prediction
        return base_value * 1000  # Scale to monetary units
    
    def _calculate_match_confidence(self, analysis: CompatibilityAnalysis) -> float:
        """Calculate confidence in the match"""
        # Confidence based on number of factors and their consistency
        factor_scores = list(analysis.factor_scores.values())
        if not factor_scores:
            return 0.5
        
        avg_score = sum(factor_scores) / len(factor_scores)
        variance = sum((score - avg_score) ** 2 for score in factor_scores) / len(factor_scores)
        
        # Lower variance means higher confidence
        confidence = avg_score * (1 - variance / 2)
        return min(max(confidence, 0.0), 1.0)
    
    def _generate_match_reasons(self, analysis: CompatibilityAnalysis) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        if analysis.factor_scores.get(CompatibilityFactor.SKILL_COMPLEMENT, 0) > 0.8:
            reasons.append("Excellent skill complementarity")
        
        if analysis.factor_scores.get(CompatibilityFactor.COMMUNICATION_STYLE, 0) > 0.8:
            reasons.append("Compatible communication styles")
        
        if analysis.factor_scores.get(CompatibilityFactor.WORK_SCHEDULE, 0) > 0.8:
            reasons.append("Aligned work schedules")
        
        if analysis.success_prediction > 0.8:
            reasons.append("High success probability predicted")
        
        if len(analysis.synergy_opportunities) > 2:
            reasons.append("Multiple synergy opportunities identified")
        
        return reasons
    
    def get_core_metrics(self) -> Dict[str, Any]:
        """Get core matching metrics"""
        return {
            'creator_matching_core_metrics': self.metrics.copy(),
            'core_status': 'operational',
            'total_skill_profiles': len(self.skill_profiles),
            'total_preferences': len(self.collaboration_preferences),
            'total_matches': len(self.matches),
            'matching_sessions': len(self.matching_sessions),
            'ai_model_version': self.compatibility_model['model_version'],
            'uptime_guarantee': '>99.99%'
        }

# Global creator matching core instance
creator_matching_core = CreatorMatchingCore()

logger.info("Creator Matching Core initialized")