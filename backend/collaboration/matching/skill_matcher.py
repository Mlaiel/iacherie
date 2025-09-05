"""Skill Matcher Module - Advanced Skill Complementarity Analysis System
========================================================================

Sophisticated skill analysis and matching system for identifying optimal creator
skill combinations, complementarity gaps, and collaboration potential based on
technical abilities, creative skills, and professional competencies.

This module implements:
- Multi-dimensional skill profiling and analysis
- Skill complementarity and gap detection
- Professional competency assessment
- Skill-based collaboration optimization
- Learning and development recommendations

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
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import statistics

logger = logging.getLogger(__name__)


class SkillCategory(Enum):
    """Categories of skills for creators"""
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BUSINESS = "business"
    COMMUNICATION = "communication"
    MARKETING = "marketing"
    PRODUCTION = "production"
    ANALYTICAL = "analytical"
    LEADERSHIP = "leadership"
    DESIGN = "design"
    AUDIO = "audio"
    VIDEO = "video"
    WRITING = "writing"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5


class ComplementarityType(Enum):
    """Types of skill complementarity"""
    PERFECT_COMPLEMENT = "perfect_complement"  # Skills that work perfectly together
    STRONG_COMPLEMENT = "strong_complement"    # Skills that enhance each other
    MODERATE_COMPLEMENT = "moderate_complement" # Some synergy
    OVERLAP = "overlap"                        # Similar skills (redundant)
    INDEPENDENT = "independent"                # Unrelated skills
    CONFLICTING = "conflicting"               # Skills that may conflict


@dataclass
class Skill:
    """Individual skill representation"""
    name: str
    category: SkillCategory
    level: SkillLevel
    years_experience: float
    certifications: List[str] = field(default_factory=list)
    portfolio_examples: List[str] = field(default_factory=list)
    endorsements: int = 0
    self_assessment_score: float = 0.0
    peer_assessment_score: float = 0.0
    verified: bool = False
    last_used: Optional[datetime] = None
    learning_trajectory: Optional[str] = None  # "improving", "stable", "declining"
    
    @property
    def effective_level(self) -> float:
        """Calculate effective skill level considering all factors"""
        base_level = self.level.value
        
        # Adjust based on experience
        experience_bonus = min(self.years_experience / 5.0, 1.0) * 0.5
        
        # Adjust based on assessments
        assessment_avg = (self.self_assessment_score + self.peer_assessment_score) / 2
        assessment_adjustment = (assessment_avg - 0.5) * 0.3
        
        # Verification bonus
        verification_bonus = 0.2 if self.verified else 0.0
        
        # Recent usage penalty
        if self.last_used:
            days_since_use = (datetime.now(timezone.utc) - self.last_used).days
            recency_penalty = min(days_since_use / 365.0, 0.5) * -0.2
        else:
            recency_penalty = -0.1
        
        effective = base_level + experience_bonus + assessment_adjustment + verification_bonus + recency_penalty
        return max(1.0, min(5.0, effective))


@dataclass
class SkillProfile:
    """Comprehensive skill profile for a creator"""
    creator_id: str
    skills: List[Skill]
    skill_categories: Dict[SkillCategory, float]  # Average proficiency per category
    strengths: List[SkillCategory]
    weaknesses: List[SkillCategory]
    learning_preferences: List[str]
    skill_development_goals: List[str]
    collaboration_preferences: Dict[str, Any]
    skill_verification_score: float
    skill_diversity_index: float
    skill_depth_index: float
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a specific category"""
        return [skill for skill in self.skills if skill.category == category]
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        for skill in self.skills:
            if skill.name.lower() == name.lower():
                return skill
        return None
    
    def has_skill(self, name: str, min_level: SkillLevel = SkillLevel.BEGINNER) -> bool:
        """Check if creator has a skill at minimum level"""
        skill = self.get_skill_by_name(name)
        return skill is not None and skill.level.value >= min_level.value


@dataclass
class SkillGap:
    """Represents a skill gap in collaboration"""
    skill_name: str
    category: SkillCategory
    required_level: SkillLevel
    current_level: Optional[SkillLevel]
    gap_severity: float  # 0-1, higher = more critical
    impact_on_collaboration: str
    mitigation_strategies: List[str]
    learning_resources: List[str]
    estimated_learning_time: int  # days


@dataclass
class ComplementarySkills:
    """Analysis of skill complementarity between creators"""
    skill_pairs: List[Tuple[Skill, Skill]]
    complementarity_type: ComplementarityType
    synergy_score: float
    coverage_improvement: float
    collaboration_potential: float
    recommended_projects: List[str]
    success_factors: List[str]


@dataclass
class SkillCompatibility:
    """Overall skill compatibility between creators"""
    creator_ids: List[str]
    overall_compatibility_score: float
    skill_overlap_analysis: Dict[SkillCategory, float]
    complementarity_analysis: List[ComplementarySkills]
    identified_gaps: List[SkillGap]
    collaboration_strengths: List[str]
    potential_challenges: List[str]
    recommended_skill_development: Dict[str, List[str]]  # creator_id -> skills to develop
    project_recommendations: List[Dict[str, Any]]
    confidence_score: float


class SkillMatcher:
    """Advanced skill matching and complementarity analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the skill matcher"""
        self.config = config or {}
        self.skill_relationships = self._initialize_skill_relationships()
        self.complementarity_matrix = self._build_complementarity_matrix()
        self.project_skill_requirements = self._load_project_skill_requirements()
        
        logger.info("🎯 Skill Matcher initialized")
    
    def _initialize_skill_relationships(self) -> Dict[str, Dict[str, float]]:
        """Initialize relationships between different skills"""
        # Simplified skill relationship matrix
        # In production, this would be learned from data
        relationships = {
            # Video production skills
            "video_editing": {
                "motion_graphics": 0.8,
                "color_grading": 0.9,
                "audio_mixing": 0.7,
                "storytelling": 0.8,
                "cinematography": 0.6
            },
            
            # Audio skills
            "audio_production": {
                "music_composition": 0.9,
                "sound_design": 0.8,
                "podcast_editing": 0.7,
                "voice_acting": 0.6
            },
            
            # Content creation
            "content_writing": {
                "copywriting": 0.8,
                "seo": 0.7,
                "storytelling": 0.9,
                "social_media_management": 0.6
            },
            
            # Design skills
            "graphic_design": {
                "ui_design": 0.7,
                "branding": 0.8,
                "illustration": 0.8,
                "web_design": 0.6
            },
            
            # Marketing skills
            "digital_marketing": {
                "social_media_marketing": 0.9,
                "content_marketing": 0.8,
                "email_marketing": 0.7,
                "analytics": 0.8
            },
            
            # Business skills
            "project_management": {
                "team_leadership": 0.8,
                "strategic_planning": 0.7,
                "budgeting": 0.8,
                "client_management": 0.7
            }
        }
        
        return relationships
    
    def _build_complementarity_matrix(self) -> Dict[Tuple[str, str], float]:
        """Build matrix of skill complementarity scores"""
        # Complementarity scores between different skills
        complementarity = {
            ("video_editing", "music_composition"): 0.9,
            ("graphic_design", "content_writing"): 0.8,
            ("social_media_marketing", "photography"): 0.9,
            ("project_management", "creative_direction"): 0.8,
            ("data_analysis", "content_strategy"): 0.7,
            ("web_development", "ui_design"): 0.9,
            ("voice_acting", "audio_production"): 0.8,
            ("animation", "storytelling"): 0.9,
            ("seo", "content_writing"): 0.8,
            ("branding", "graphic_design"): 0.7
        }
        
        # Make symmetric
        symmetric_complementarity = {}
        for (skill1, skill2), score in complementarity.items():
            symmetric_complementarity[(skill1, skill2)] = score
            symmetric_complementarity[(skill2, skill1)] = score
        
        return symmetric_complementarity
    
    def _load_project_skill_requirements(self) -> Dict[str, Dict[str, SkillLevel]]:
        """Load skill requirements for different project types"""
        return {
            "music_video": {
                "video_editing": SkillLevel.ADVANCED,
                "music_composition": SkillLevel.INTERMEDIATE,
                "cinematography": SkillLevel.INTERMEDIATE,
                "color_grading": SkillLevel.INTERMEDIATE,
                "audio_mixing": SkillLevel.ADVANCED
            },
            
            "brand_campaign": {
                "branding": SkillLevel.ADVANCED,
                "graphic_design": SkillLevel.ADVANCED,
                "copywriting": SkillLevel.INTERMEDIATE,
                "social_media_marketing": SkillLevel.ADVANCED,
                "project_management": SkillLevel.INTERMEDIATE
            },
            
            "educational_series": {
                "content_writing": SkillLevel.ADVANCED,
                "instructional_design": SkillLevel.ADVANCED,
                "video_editing": SkillLevel.INTERMEDIATE,
                "public_speaking": SkillLevel.ADVANCED,
                "curriculum_development": SkillLevel.INTERMEDIATE
            },
            
            "podcast_series": {
                "audio_production": SkillLevel.ADVANCED,
                "interviewing": SkillLevel.ADVANCED,
                "content_research": SkillLevel.INTERMEDIATE,
                "storytelling": SkillLevel.ADVANCED,
                "audio_editing": SkillLevel.ADVANCED
            },
            
            "web_series": {
                "video_production": SkillLevel.ADVANCED,
                "scriptwriting": SkillLevel.ADVANCED,
                "acting": SkillLevel.INTERMEDIATE,
                "directing": SkillLevel.INTERMEDIATE,
                "post_production": SkillLevel.ADVANCED
            }
        }
    
    async def analyze_skill_compatibility(
        self,
        profiles: List[SkillProfile]
    ) -> SkillCompatibility:
        """Analyze skill compatibility between multiple creators"""
        try:
            logger.info(f"🔍 Analyzing skill compatibility for {len(profiles)} creators")
            
            if len(profiles) < 2:
                raise ValueError("Need at least 2 skill profiles for compatibility analysis")
            
            creator_ids = [profile.creator_id for profile in profiles]
            
            # Calculate overall compatibility
            overall_score = await self._calculate_overall_compatibility(profiles)
            
            # Analyze skill overlap by category
            overlap_analysis = await self._analyze_skill_overlap(profiles)
            
            # Find complementary skills
            complementarity_analysis = await self._find_complementary_skills(profiles)
            
            # Identify skill gaps
            gaps = await self._identify_skill_gaps(profiles)
            
            # Identify collaboration strengths
            strengths = await self._identify_collaboration_strengths(profiles)
            
            # Identify potential challenges
            challenges = await self._identify_potential_challenges(profiles)
            
            # Generate skill development recommendations
            development_recommendations = await self._generate_development_recommendations(profiles, gaps)
            
            # Generate project recommendations
            project_recommendations = await self._generate_project_recommendations(profiles)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(profiles, overall_score)
            
            compatibility = SkillCompatibility(
                creator_ids=creator_ids,
                overall_compatibility_score=overall_score,
                skill_overlap_analysis=overlap_analysis,
                complementarity_analysis=complementarity_analysis,
                identified_gaps=gaps,
                collaboration_strengths=strengths,
                potential_challenges=challenges,
                recommended_skill_development=development_recommendations,
                project_recommendations=project_recommendations,
                confidence_score=confidence_score
            )
            
            logger.info(f"✅ Skill compatibility analysis completed: {overall_score:.3f}")
            return compatibility
            
        except Exception as e:
            logger.error(f"❌ Error in skill compatibility analysis: {e}")
            raise
    
    async def _calculate_overall_compatibility(self, profiles: List[SkillProfile]) -> float:
        """Calculate overall skill compatibility score"""
        compatibility_factors = []
        
        # 1. Skill coverage completeness
        all_categories = set()
        for profile in profiles:
            all_categories.update(profile.skill_categories.keys())
        
        covered_categories = 0
        for category in all_categories:
            max_proficiency = max(
                profile.skill_categories.get(category, 0) for profile in profiles
            )
            if max_proficiency >= 2.0:  # At least intermediate level
                covered_categories += 1
        
        coverage_score = covered_categories / len(all_categories) if all_categories else 0
        compatibility_factors.append(coverage_score)
        
        # 2. Complementarity score
        complementarity_scores = []
        for i, profile_a in enumerate(profiles):
            for j, profile_b in enumerate(profiles[i+1:], i+1):
                comp_score = await self._calculate_pairwise_complementarity(profile_a, profile_b)
                complementarity_scores.append(comp_score)
        
        avg_complementarity = statistics.mean(complementarity_scores) if complementarity_scores else 0.5
        compatibility_factors.append(avg_complementarity)
        
        # 3. Skill level balance
        avg_levels = []
        for profile in profiles:
            profile_avg = statistics.mean([
                skill.effective_level for skill in profile.skills
            ]) if profile.skills else 2.5
            avg_levels.append(profile_avg)
        
        level_variance = np.var(avg_levels)
        balance_score = max(0, 1 - (level_variance / 2))  # Lower variance = better balance
        compatibility_factors.append(balance_score)
        
        # 4. Diversity index
        all_skills = set()
        for profile in profiles:
            all_skills.update(skill.name for skill in profile.skills)
        
        total_skills = sum(len(profile.skills) for profile in profiles)
        diversity_score = len(all_skills) / max(total_skills, 1)
        compatibility_factors.append(diversity_score)
        
        return statistics.mean(compatibility_factors)
    
    async def _analyze_skill_overlap(self, profiles: List[SkillProfile]) -> Dict[SkillCategory, float]:
        """Analyze skill overlap by category"""
        overlap_analysis = {}
        
        all_categories = set()
        for profile in profiles:
            all_categories.update(profile.skill_categories.keys())
        
        for category in all_categories:
            # Get proficiency levels for this category across all creators
            proficiencies = [
                profile.skill_categories.get(category, 0) for profile in profiles
            ]
            
            # Calculate overlap metric
            # High overlap = multiple creators have good skills in this area
            # Low overlap = only one creator has skills in this area
            non_zero_count = sum(1 for p in proficiencies if p > 1.0)
            overlap_score = non_zero_count / len(profiles)
            
            overlap_analysis[category] = overlap_score
        
        return overlap_analysis
    
    async def _find_complementary_skills(self, profiles: List[SkillProfile]) -> List[ComplementarySkills]:
        """Find complementary skills between creators"""
        complementary_skills = []
        
        for i, profile_a in enumerate(profiles):
            for j, profile_b in enumerate(profiles[i+1:], i+1):
                # Find skill pairs with high complementarity
                for skill_a in profile_a.skills:
                    for skill_b in profile_b.skills:
                        comp_score = self.complementarity_matrix.get(
                            (skill_a.name, skill_b.name), 0.0
                        )
                        
                        if comp_score > 0.6:  # High complementarity threshold
                            # Determine complementarity type
                            if comp_score >= 0.9:
                                comp_type = ComplementarityType.PERFECT_COMPLEMENT
                            elif comp_score >= 0.7:
                                comp_type = ComplementarityType.STRONG_COMPLEMENT
                            else:
                                comp_type = ComplementarityType.MODERATE_COMPLEMENT
                            
                            # Calculate synergy score
                            synergy_score = (skill_a.effective_level + skill_b.effective_level) / 10 * comp_score
                            
                            # Calculate coverage improvement
                            coverage_improvement = min(skill_a.effective_level, skill_b.effective_level) / 5.0
                            
                            # Calculate collaboration potential
                            collaboration_potential = synergy_score * coverage_improvement
                            
                            # Generate recommendations
                            project_recommendations = self._get_skill_pair_projects(skill_a.name, skill_b.name)
                            success_factors = self._get_success_factors(skill_a, skill_b)
                            
                            complementary = ComplementarySkills(
                                skill_pairs=[(skill_a, skill_b)],
                                complementarity_type=comp_type,
                                synergy_score=synergy_score,
                                coverage_improvement=coverage_improvement,
                                collaboration_potential=collaboration_potential,
                                recommended_projects=project_recommendations,
                                success_factors=success_factors
                            )
                            
                            complementary_skills.append(complementary)
        
        # Sort by collaboration potential
        complementary_skills.sort(key=lambda x: x.collaboration_potential, reverse=True)
        
        return complementary_skills[:10]  # Return top 10
    
    async def _calculate_pairwise_complementarity(
        self,
        profile_a: SkillProfile,
        profile_b: SkillProfile
    ) -> float:
        """Calculate complementarity score between two skill profiles"""
        complementarity_scores = []
        
        # Check each skill in profile A against profile B
        for skill_a in profile_a.skills:
            best_complement_score = 0.0
            
            for skill_b in profile_b.skills:
                comp_score = self.complementarity_matrix.get(
                    (skill_a.name, skill_b.name), 0.0
                )
                
                # Adjust for skill levels
                level_factor = min(skill_a.effective_level, skill_b.effective_level) / 5.0
                adjusted_score = comp_score * level_factor
                
                best_complement_score = max(best_complement_score, adjusted_score)
            
            complementarity_scores.append(best_complement_score)
        
        # Also check profile B against profile A
        for skill_b in profile_b.skills:
            best_complement_score = 0.0
            
            for skill_a in profile_a.skills:
                comp_score = self.complementarity_matrix.get(
                    (skill_b.name, skill_a.name), 0.0
                )
                
                level_factor = min(skill_a.effective_level, skill_b.effective_level) / 5.0
                adjusted_score = comp_score * level_factor
                
                best_complement_score = max(best_complement_score, adjusted_score)
            
            complementarity_scores.append(best_complement_score)
        
        return statistics.mean(complementarity_scores) if complementarity_scores else 0.0
    
    async def _identify_skill_gaps(self, profiles: List[SkillProfile]) -> List[SkillGap]:
        """Identify skill gaps for different project types"""
        gaps = []
        
        # Combine all skills from all profiles
        all_skills = {}
        for profile in profiles:
            for skill in profile.skills:
                if skill.name not in all_skills:
                    all_skills[skill.name] = skill
                else:
                    # Keep the highest level
                    if skill.effective_level > all_skills[skill.name].effective_level:
                        all_skills[skill.name] = skill
        
        # Check against project requirements
        for project_type, requirements in self.project_skill_requirements.items():
            for required_skill, required_level in requirements.items():
                current_skill = all_skills.get(required_skill)
                
                if current_skill is None:
                    # Complete gap
                    gap = SkillGap(
                        skill_name=required_skill,
                        category=self._get_skill_category(required_skill),
                        required_level=required_level,
                        current_level=None,
                        gap_severity=1.0,
                        impact_on_collaboration=f"Cannot execute {project_type} without {required_skill}",
                        mitigation_strategies=[
                            "Hire specialist",
                            "Outsource this component",
                            "Learn basic skills quickly"
                        ],
                        learning_resources=[
                            f"Online {required_skill} courses",
                            f"{required_skill} workshops",
                            f"Mentorship in {required_skill}"
                        ],
                        estimated_learning_time=self._estimate_learning_time(required_level)
                    )
                    gaps.append(gap)
                
                elif current_skill.level.value < required_level.value:
                    # Partial gap
                    gap_severity = (required_level.value - current_skill.level.value) / 4.0
                    
                    gap = SkillGap(
                        skill_name=required_skill,
                        category=current_skill.category,
                        required_level=required_level,
                        current_level=current_skill.level,
                        gap_severity=gap_severity,
                        impact_on_collaboration=f"Suboptimal {project_type} execution due to skill level gap",
                        mitigation_strategies=[
                            "Focused skill development",
                            "Pair with experienced mentor",
                            "Practice with smaller projects first"
                        ],
                        learning_resources=[
                            f"Advanced {required_skill} training",
                            f"{required_skill} certification programs",
                            f"Practical {required_skill} projects"
                        ],
                        estimated_learning_time=self._estimate_improvement_time(
                            current_skill.level, required_level
                        )
                    )
                    gaps.append(gap)
        
        # Sort by severity
        gaps.sort(key=lambda x: x.gap_severity, reverse=True)
        
        return gaps
    
    def _get_skill_category(self, skill_name: str) -> SkillCategory:
        """Get category for a skill name (simplified mapping)"""
        skill_category_mapping = {
            "video_editing": SkillCategory.VIDEO,
            "audio_production": SkillCategory.AUDIO,
            "graphic_design": SkillCategory.DESIGN,
            "content_writing": SkillCategory.WRITING,
            "project_management": SkillCategory.BUSINESS,
            "social_media_marketing": SkillCategory.MARKETING,
            "data_analysis": SkillCategory.ANALYTICAL,
            "music_composition": SkillCategory.AUDIO,
            "photography": SkillCategory.PRODUCTION,
            "public_speaking": SkillCategory.COMMUNICATION
        }
        
        return skill_category_mapping.get(skill_name, SkillCategory.TECHNICAL)
    
    def _estimate_learning_time(self, target_level: SkillLevel) -> int:
        """Estimate time in days to learn a skill to target level"""
        base_times = {
            SkillLevel.BEGINNER: 30,
            SkillLevel.INTERMEDIATE: 90,
            SkillLevel.ADVANCED: 180,
            SkillLevel.EXPERT: 365,
            SkillLevel.MASTER: 730
        }
        
        return base_times.get(target_level, 90)
    
    def _estimate_improvement_time(self, current_level: SkillLevel, target_level: SkillLevel) -> int:
        """Estimate time to improve from current to target level"""
        level_gap = target_level.value - current_level.value
        base_time = 60  # days per level
        return level_gap * base_time
    
    async def _identify_collaboration_strengths(self, profiles: List[SkillProfile]) -> List[str]:
        """Identify collaboration strengths based on combined skills"""
        strengths = []
        
        # Combined skill categories
        all_categories = set()
        for profile in profiles:
            all_categories.update(profile.skill_categories.keys())
        
        strong_categories = []
        for category in all_categories:
            max_proficiency = max(
                profile.skill_categories.get(category, 0) for profile in profiles
            )
            if max_proficiency >= 3.0:  # Advanced level or higher
                strong_categories.append(category)
        
        # Generate strength descriptions
        if SkillCategory.VIDEO in strong_categories and SkillCategory.AUDIO in strong_categories:
            strengths.append("Excellent multimedia production capabilities")
        
        if SkillCategory.DESIGN in strong_categories and SkillCategory.MARKETING in strong_categories:
            strengths.append("Strong visual marketing and branding potential")
        
        if SkillCategory.WRITING in strong_categories and SkillCategory.COMMUNICATION in strong_categories:
            strengths.append("Exceptional content creation and communication skills")
        
        if SkillCategory.TECHNICAL in strong_categories and SkillCategory.CREATIVE in strong_categories:
            strengths.append("Powerful combination of technical and creative abilities")
        
        if SkillCategory.BUSINESS in strong_categories and SkillCategory.ANALYTICAL in strong_categories:
            strengths.append("Data-driven business strategy capabilities")
        
        # Check for skill diversity
        if len(strong_categories) >= 4:
            strengths.append("Highly diverse skill set enabling versatile collaborations")
        
        # Check for complementarity
        complementarity_scores = []
        for i, profile_a in enumerate(profiles):
            for j, profile_b in enumerate(profiles[i+1:], i+1):
                comp_score = await self._calculate_pairwise_complementarity(profile_a, profile_b)
                complementarity_scores.append(comp_score)
        
        if complementarity_scores and statistics.mean(complementarity_scores) > 0.7:
            strengths.append("Highly complementary skill sets with strong synergy potential")
        
        return strengths
    
    async def _identify_potential_challenges(self, profiles: List[SkillProfile]) -> List[str]:
        """Identify potential challenges in collaboration"""
        challenges = []
        
        # Skill level imbalances
        all_skill_levels = []
        for profile in profiles:
            avg_level = statistics.mean([skill.effective_level for skill in profile.skills])
            all_skill_levels.append(avg_level)
        
        if len(all_skill_levels) > 1:
            level_variance = np.var(all_skill_levels)
            if level_variance > 1.0:
                challenges.append("Significant skill level imbalance between creators")
        
        # Skill overlap issues
        overlap_analysis = await self._analyze_skill_overlap(profiles)
        high_overlap_categories = [
            cat for cat, overlap in overlap_analysis.items() if overlap > 0.8
        ]
        
        if len(high_overlap_categories) > 2:
            challenges.append("Excessive skill overlap may lead to redundancy")
        
        # Gap analysis
        gaps = await self._identify_skill_gaps(profiles)
        critical_gaps = [gap for gap in gaps if gap.gap_severity > 0.7]
        
        if len(critical_gaps) > 3:
            challenges.append("Multiple critical skill gaps may limit project scope")
        
        # Specialization vs generalization
        specialists = 0
        generalists = 0
        
        for profile in profiles:
            skill_count = len(profile.skills)
            max_level = max([skill.effective_level for skill in profile.skills]) if profile.skills else 0
            
            if skill_count <= 5 and max_level >= 4.0:
                specialists += 1
            elif skill_count >= 10 and max_level <= 3.5:
                generalists += 1
        
        if specialists > 0 and generalists > 0:
            challenges.append("Mixed specialist and generalist approaches may require coordination")
        
        # Communication and leadership
        communication_skills = []
        leadership_skills = []
        
        for profile in profiles:
            comm_skills = profile.get_skills_by_category(SkillCategory.COMMUNICATION)
            lead_skills = profile.get_skills_by_category(SkillCategory.LEADERSHIP)
            
            communication_skills.extend(comm_skills)
            leadership_skills.extend(lead_skills)
        
        if not leadership_skills:
            challenges.append("No clear leadership skills identified for project coordination")
        
        if len(communication_skills) < len(profiles):
            challenges.append("Communication skills may be insufficient for effective collaboration")
        
        return challenges
    
    async def _generate_development_recommendations(
        self,
        profiles: List[SkillProfile],
        gaps: List[SkillGap]
    ) -> Dict[str, List[str]]:
        """Generate skill development recommendations for each creator"""
        recommendations = {}
        
        for profile in profiles:
            creator_recommendations = []
            
            # Based on identified gaps
            relevant_gaps = [
                gap for gap in gaps 
                if gap.estimated_learning_time <= 180  # Learnable within 6 months
            ]
            
            for gap in relevant_gaps[:3]:  # Top 3 most critical learnable gaps
                creator_recommendations.append(
                    f"Develop {gap.skill_name} to {gap.required_level.name} level"
                )
            
            # Based on existing strengths (deepen expertise)
            strong_skills = [
                skill for skill in profile.skills 
                if skill.effective_level >= 3.0 and skill.level != SkillLevel.MASTER
            ]
            
            if strong_skills:
                best_skill = max(strong_skills, key=lambda s: s.effective_level)
                creator_recommendations.append(
                    f"Advance {best_skill.name} to expert/master level"
                )
            
            # Based on complementarity opportunities
            for other_profile in profiles:
                if other_profile.creator_id != profile.creator_id:
                    comp_score = await self._calculate_pairwise_complementarity(profile, other_profile)
                    if comp_score < 0.5:  # Low complementarity, could be improved
                        # Find skills in other_profile that would complement profile
                        for other_skill in other_profile.skills:
                            if other_skill.effective_level >= 3.0:
                                # Check if learning this skill would create complementarity
                                potential_comp = self.complementarity_matrix.get(
                                    (other_skill.name, profile.skills[0].name if profile.skills else ""), 0.0
                                )
                                if potential_comp > 0.6:
                                    creator_recommendations.append(
                                        f"Learn {other_skill.name} to complement {other_profile.creator_id}'s expertise"
                                    )
                                    break
            
            # Remove duplicates and limit to top 5
            unique_recommendations = list(dict.fromkeys(creator_recommendations))
            recommendations[profile.creator_id] = unique_recommendations[:5]
        
        return recommendations
    
    async def _generate_project_recommendations(self, profiles: List[SkillProfile]) -> List[Dict[str, Any]]:
        """Generate project recommendations based on combined skills"""
        recommendations = []
        
        # Combine all skills
        all_skills = set()
        skill_levels = {}
        
        for profile in profiles:
            for skill in profile.skills:
                all_skills.add(skill.name)
                current_level = skill_levels.get(skill.name, 0)
                skill_levels[skill.name] = max(current_level, skill.effective_level)
        
        # Check each project type
        for project_type, requirements in self.project_skill_requirements.items():
            skill_coverage = 0
            total_requirements = len(requirements)
            quality_score = 0
            
            for required_skill, required_level in requirements.items():
                if required_skill in skill_levels:
                    current_level = skill_levels[required_skill]
                    if current_level >= required_level.value:
                        skill_coverage += 1
                        # Quality bonus for exceeding requirements
                        quality_score += min(current_level - required_level.value, 2) * 0.1
                    else:
                        # Partial credit for having some level
                        partial_coverage = current_level / required_level.value
                        skill_coverage += partial_coverage
            
            coverage_ratio = skill_coverage / total_requirements
            overall_score = coverage_ratio + quality_score
            
            if coverage_ratio >= 0.7:  # At least 70% skill coverage
                feasibility = "High" if coverage_ratio >= 0.9 else "Medium"
                
                recommendation = {
                    "project_type": project_type,
                    "feasibility": feasibility,
                    "skill_coverage": coverage_ratio,
                    "quality_score": overall_score,
                    "missing_skills": [
                        skill for skill, level in requirements.items()
                        if skill not in skill_levels or skill_levels[skill] < level.value
                    ],
                    "advantages": self._get_project_advantages(project_type, skill_levels),
                    "success_probability": min(overall_score / 1.5, 1.0)
                }
                
                recommendations.append(recommendation)
        
        # Sort by success probability
        recommendations.sort(key=lambda x: x["success_probability"], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _get_skill_pair_projects(self, skill_a: str, skill_b: str) -> List[str]:
        """Get project recommendations for specific skill pairs"""
        skill_pair_projects = {
            ("video_editing", "music_composition"): ["music_video", "commercial", "short_film"],
            ("graphic_design", "content_writing"): ["brand_campaign", "blog_series", "infographic_series"],
            ("audio_production", "voice_acting"): ["podcast_series", "audiobook", "commercial_voice_over"],
            ("photography", "social_media_marketing"): ["brand_photography", "influencer_campaign", "product_showcase"],
            ("web_development", "ui_design"): ["website_project", "app_development", "digital_platform"]
        }
        
        return skill_pair_projects.get((skill_a, skill_b), 
               skill_pair_projects.get((skill_b, skill_a), ["collaborative_project"]))
    
    def _get_success_factors(self, skill_a: Skill, skill_b: Skill) -> List[str]:
        """Get success factors for skill combination"""
        factors = []
        
        # Level compatibility
        level_diff = abs(skill_a.effective_level - skill_b.effective_level)
        if level_diff <= 1.0:
            factors.append("Similar skill levels enable balanced collaboration")
        
        # Experience compatibility
        exp_diff = abs(skill_a.years_experience - skill_b.years_experience)
        if exp_diff <= 2.0:
            factors.append("Comparable experience levels")
        
        # Recent usage
        if skill_a.last_used and skill_b.last_used:
            days_diff = abs((skill_a.last_used - skill_b.last_used).days)
            if days_diff <= 90:
                factors.append("Both skills recently active")
        
        # Verification status
        if skill_a.verified and skill_b.verified:
            factors.append("Both skills professionally verified")
        
        return factors if factors else ["Potential for good collaboration"]
    
    def _get_project_advantages(self, project_type: str, skill_levels: Dict[str, float]) -> List[str]:
        """Get advantages for specific project type"""
        advantages = []
        
        if project_type == "music_video":
            if skill_levels.get("cinematography", 0) >= 4.0:
                advantages.append("Exceptional cinematography capabilities")
            if skill_levels.get("audio_mixing", 0) >= 4.0:
                advantages.append("Professional audio production")
        
        elif project_type == "brand_campaign":
            if skill_levels.get("branding", 0) >= 4.0:
                advantages.append("Strong brand strategy expertise")
            if skill_levels.get("digital_marketing", 0) >= 4.0:
                advantages.append("Comprehensive digital marketing reach")
        
        elif project_type == "educational_series":
            if skill_levels.get("instructional_design", 0) >= 4.0:
                advantages.append("Professional instructional design")
            if skill_levels.get("curriculum_development", 0) >= 4.0:
                advantages.append("Structured curriculum planning")
        
        return advantages if advantages else ["Solid foundation for success"]
    
    async def _calculate_confidence_score(
        self,
        profiles: List[SkillProfile],
        overall_score: float
    ) -> float:
        """Calculate confidence in the compatibility analysis"""
        confidence_factors = []
        
        # Data completeness
        total_skills = sum(len(profile.skills) for profile in profiles)
        avg_skills_per_creator = total_skills / len(profiles)
        completeness_score = min(avg_skills_per_creator / 10.0, 1.0)  # Assume 10 skills = complete
        confidence_factors.append(completeness_score)
        
        # Skill verification
        verified_skills = sum(
            sum(1 for skill in profile.skills if skill.verified)
            for profile in profiles
        )
        verification_score = verified_skills / max(total_skills, 1)
        confidence_factors.append(verification_score)
        
        # Recent activity
        recent_skills = sum(
            sum(1 for skill in profile.skills 
                if skill.last_used and (datetime.now(timezone.utc) - skill.last_used).days <= 90)
            for profile in profiles
        )
        recency_score = recent_skills / max(total_skills, 1)
        confidence_factors.append(recency_score)
        
        # Assessment availability
        assessed_skills = sum(
            sum(1 for skill in profile.skills 
                if skill.peer_assessment_score > 0 or skill.self_assessment_score > 0)
            for profile in profiles
        )
        assessment_score = assessed_skills / max(total_skills, 1)
        confidence_factors.append(assessment_score)
        
        return statistics.mean(confidence_factors)


# Export main classes
__all__ = [
    'SkillMatcher',
    'SkillProfile',
    'SkillCompatibility',
    'SkillGap',
    'ComplementarySkills',
    'Skill',
    'SkillCategory',
    'SkillLevel',
    'ComplementarityType'
]