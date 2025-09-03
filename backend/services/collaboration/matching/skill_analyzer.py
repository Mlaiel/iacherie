"""Skill Analyzer - Advanced Creator Skill Analysis Engine

Advanced skill analysis system for creator profiling and collaboration optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class SkillCategory(Enum):
    """Categories of skills"""
    TECHNICAL = "technical"
    CREATIVE = "creative"
    COMMUNICATION = "communication"
    MARKETING = "marketing"
    BUSINESS = "business"
    SOFTWARE = "software"
    EQUIPMENT = "equipment"
    ARTISTIC = "artistic"
    ANALYTICAL = "analytical"
    LEADERSHIP = "leadership"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class SkillVerificationStatus(Enum):
    """Skill verification status"""
    UNVERIFIED = "unverified"
    SELF_REPORTED = "self_reported"
    PEER_VERIFIED = "peer_verified"
    CERTIFIED = "certified"
    PROFESSIONALLY_VERIFIED = "professionally_verified"


@dataclass
class Skill:
    """Individual skill representation"""
    skill_id: str
    name: str
    category: SkillCategory
    level: SkillLevel
    verification_status: SkillVerificationStatus
    years_experience: float
    last_used: datetime
    endorsements: int = 0
    certifications: List[str] = field(default_factory=list)
    projects_used_in: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    market_demand: float = 0.0
    complementary_skills: List[str] = field(default_factory=list)


@dataclass
class SkillProfile:
    """Comprehensive skill profile for a creator"""
    creator_id: str
    skills: List[Skill]
    skill_summary: Dict[str, Any]
    strengths: List[str]
    growth_areas: List[str]
    recommended_skills: List[str]
    skill_score: float
    versatility_score: float
    specialization_score: float
    market_alignment_score: float
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SkillAnalysis:
    """Detailed skill analysis result"""
    analysis_id: str
    creator_id: str
    skill_gaps: List[str]
    skill_overlaps: List[str]
    recommended_learning_path: List[str]
    market_opportunities: List[str]
    collaboration_potential: Dict[str, float]
    skill_trends: Dict[str, Any]
    competitive_advantages: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SkillMatchingResult:
    """Result of skill matching between creators"""
    match_id: str
    creator_a_id: str
    creator_b_id: str
    skill_compatibility_score: float
    complementary_skills: List[str]
    overlapping_skills: List[str]
    skill_gaps: List[str]
    collaboration_potential: str
    recommended_roles: Dict[str, List[str]]
    skill_exchange_opportunities: List[str]


class SkillAnalyzer:
    """Advanced creator skill analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.skill_database = {}
        self.skill_taxonomy = self._initialize_skill_taxonomy()
        self.market_trends = {}
        self.skill_demand_data = {}
        
        logger.info("SkillAnalyzer initialized with advanced skill analysis capabilities")
    
    async def initialize(self):
        """Initialize the skill analysis engine"""
        logger.info("Initializing Skill Analyzer...")
        await self._load_skill_database()
        await self._load_market_trends()
        await self._load_skill_demand_data()
        logger.info("Skill Analyzer initialized successfully")
    
    async def shutdown(self):
        """Shutdown the skill analysis engine"""
        logger.info("Shutting down Skill Analyzer...")
        # Cleanup resources
        logger.info("Skill Analyzer shutdown complete")
    
    async def analyze_creator_skills(self, creator_id: str, skills_data: Dict[str, Any]) -> SkillProfile:
        """Analyze and profile creator skills"""
        try:
            logger.info(f"Analyzing skills for creator {creator_id}")
            
            # Parse and categorize skills
            skills = await self._parse_skills(skills_data)
            
            # Analyze skill distribution
            skill_summary = await self._generate_skill_summary(skills)
            
            # Identify strengths and growth areas
            strengths = await self._identify_strengths(skills)
            growth_areas = await self._identify_growth_areas(skills)
            
            # Generate recommendations
            recommended_skills = await self._recommend_skills(skills, skill_summary)
            
            # Calculate scores
            skill_score = await self._calculate_skill_score(skills)
            versatility_score = await self._calculate_versatility_score(skills)
            specialization_score = await self._calculate_specialization_score(skills)
            market_alignment_score = await self._calculate_market_alignment_score(skills)
            
            skill_profile = SkillProfile(
                creator_id=creator_id,
                skills=skills,
                skill_summary=skill_summary,
                strengths=strengths,
                growth_areas=growth_areas,
                recommended_skills=recommended_skills,
                skill_score=skill_score,
                versatility_score=versatility_score,
                specialization_score=specialization_score,
                market_alignment_score=market_alignment_score
            )
            
            # Store in database
            self.skill_database[creator_id] = skill_profile
            
            logger.info(f"Skill analysis completed for creator {creator_id}")
            return skill_profile
            
        except Exception as e:
            logger.error(f"Error analyzing creator skills: {str(e)}")
            raise
    
    async def perform_detailed_analysis(self, creator_id: str) -> SkillAnalysis:
        """Perform detailed skill analysis for a creator"""
        try:
            skill_profile = self.skill_database.get(creator_id)
            if not skill_profile:
                raise ValueError(f"No skill profile found for creator {creator_id}")
            
            # Identify skill gaps
            skill_gaps = await self._identify_skill_gaps(skill_profile)
            
            # Find skill overlaps with market demands
            skill_overlaps = await self._find_skill_overlaps(skill_profile)
            
            # Generate learning path
            learning_path = await self._generate_learning_path(skill_profile, skill_gaps)
            
            # Identify market opportunities
            market_opportunities = await self._identify_market_opportunities(skill_profile)
            
            # Calculate collaboration potential
            collaboration_potential = await self._calculate_collaboration_potential(skill_profile)
            
            # Analyze skill trends
            skill_trends = await self._analyze_skill_trends(skill_profile)
            
            # Identify competitive advantages
            competitive_advantages = await self._identify_competitive_advantages(skill_profile)
            
            analysis = SkillAnalysis(
                analysis_id=f"analysis_{creator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                creator_id=creator_id,
                skill_gaps=skill_gaps,
                skill_overlaps=skill_overlaps,
                recommended_learning_path=learning_path,
                market_opportunities=market_opportunities,
                collaboration_potential=collaboration_potential,
                skill_trends=skill_trends,
                competitive_advantages=competitive_advantages
            )
            
            logger.info(f"Detailed skill analysis completed for creator {creator_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing detailed skill analysis: {str(e)}")
            raise
    
    async def match_creator_skills(self, creator_a_id: str, creator_b_id: str) -> SkillMatchingResult:
        """Match skills between two creators for collaboration assessment"""
        try:
            profile_a = self.skill_database.get(creator_a_id)
            profile_b = self.skill_database.get(creator_b_id)
            
            if not profile_a or not profile_b:
                raise ValueError("Skill profiles not found for one or both creators")
            
            # Calculate skill compatibility
            compatibility_score = await self._calculate_skill_compatibility(profile_a, profile_b)
            
            # Find complementary skills
            complementary_skills = await self._find_complementary_skills(profile_a, profile_b)
            
            # Find overlapping skills
            overlapping_skills = await self._find_overlapping_skills(profile_a, profile_b)
            
            # Identify skill gaps
            skill_gaps = await self._identify_collaboration_skill_gaps(profile_a, profile_b)
            
            # Assess collaboration potential
            collaboration_potential = await self._assess_collaboration_potential(profile_a, profile_b)
            
            # Recommend roles
            recommended_roles = await self._recommend_collaboration_roles(profile_a, profile_b)
            
            # Identify skill exchange opportunities
            exchange_opportunities = await self._identify_skill_exchange_opportunities(profile_a, profile_b)
            
            result = SkillMatchingResult(
                match_id=f"skill_match_{creator_a_id}_{creator_b_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                creator_a_id=creator_a_id,
                creator_b_id=creator_b_id,
                skill_compatibility_score=compatibility_score,
                complementary_skills=complementary_skills,
                overlapping_skills=overlapping_skills,
                skill_gaps=skill_gaps,
                collaboration_potential=collaboration_potential,
                recommended_roles=recommended_roles,
                skill_exchange_opportunities=exchange_opportunities
            )
            
            logger.info(f"Skill matching completed between {creator_a_id} and {creator_b_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching creator skills: {str(e)}")
            raise
    
    def _initialize_skill_taxonomy(self) -> Dict[str, Any]:
        """Initialize skill taxonomy and relationships"""
        return {
            SkillCategory.TECHNICAL.value: [
                "Programming", "Web Development", "Mobile Development", "Data Analysis",
                "Machine Learning", "AI", "Blockchain", "Cybersecurity", "Cloud Computing"
            ],
            SkillCategory.CREATIVE.value: [
                "Graphic Design", "Video Editing", "Audio Production", "Photography",
                "Illustration", "Animation", "UI/UX Design", "Creative Writing", "Storytelling"
            ],
            SkillCategory.COMMUNICATION.value: [
                "Public Speaking", "Presentation", "Writing", "Social Media Management",
                "Content Creation", "Interviewing", "Podcasting", "Live Streaming"
            ],
            SkillCategory.MARKETING.value: [
                "Digital Marketing", "SEO", "SEM", "Social Media Marketing", "Content Marketing",
                "Email Marketing", "Influencer Marketing", "Brand Management", "Analytics"
            ],
            SkillCategory.BUSINESS.value: [
                "Project Management", "Strategic Planning", "Financial Planning", "Negotiation",
                "Leadership", "Team Management", "Business Development", "Sales"
            ],
            SkillCategory.SOFTWARE.value: [
                "Adobe Creative Suite", "Final Cut Pro", "Logic Pro", "Ableton Live",
                "WordPress", "Canva", "Figma", "Slack", "Trello", "Asana"
            ],
            SkillCategory.EQUIPMENT.value: [
                "Camera Operation", "Audio Equipment", "Lighting Setup", "Streaming Equipment",
                "Studio Setup", "Mobile Recording", "Live Production", "Post-Production"
            ],
            SkillCategory.ARTISTIC.value: [
                "Music Composition", "Songwriting", "Instrumental Performance", "Vocal Performance",
                "Dance", "Acting", "Comedy", "Visual Arts", "Crafts"
            ],
            SkillCategory.ANALYTICAL.value: [
                "Data Analysis", "Market Research", "Performance Analytics", "A/B Testing",
                "Reporting", "Trend Analysis", "Competitive Analysis", "ROI Analysis"
            ],
            SkillCategory.LEADERSHIP.value: [
                "Team Leadership", "Mentoring", "Decision Making", "Conflict Resolution",
                "Change Management", "Strategic Thinking", "Vision Setting", "Coaching"
            ]
        }
    
    async def _load_skill_database(self):
        """Load existing skill profiles from database"""
        # In real implementation, load from database
        logger.info("Loading skill database...")
    
    async def _load_market_trends(self):
        """Load current market trends for skills"""
        # In real implementation, load from market data APIs
        self.market_trends = {
            "trending_up": ["AI", "Machine Learning", "TikTok Marketing", "Short-form Video"],
            "trending_down": ["Flash Development", "Traditional Advertising"],
            "stable": ["Photography", "Video Editing", "Graphic Design", "Writing"]
        }
        logger.info("Market trends loaded")
    
    async def _load_skill_demand_data(self):
        """Load skill demand data from market"""
        # In real implementation, integrate with job market APIs
        self.skill_demand_data = {
            "high_demand": ["Video Editing", "Social Media Management", "Content Creation"],
            "medium_demand": ["Photography", "Graphic Design", "Writing"],
            "low_demand": ["Traditional Radio", "Print Design"]
        }
        logger.info("Skill demand data loaded")
    
    async def _parse_skills(self, skills_data: Dict[str, Any]) -> List[Skill]:
        """Parse and structure skills data"""
        skills = []
        
        for skill_name, skill_info in skills_data.items():
            # Determine skill category
            category = self._categorize_skill(skill_name)
            
            # Parse skill level
            level = SkillLevel(skill_info.get('level', 'intermediate'))
            
            # Parse verification status
            verification = SkillVerificationStatus(skill_info.get('verification', 'self_reported'))
            
            skill = Skill(
                skill_id=f"skill_{skill_name.lower().replace(' ', '_')}",
                name=skill_name,
                category=category,
                level=level,
                verification_status=verification,
                years_experience=skill_info.get('years_experience', 1.0),
                last_used=datetime.fromisoformat(skill_info.get('last_used', datetime.now().isoformat())),
                endorsements=skill_info.get('endorsements', 0),
                certifications=skill_info.get('certifications', []),
                projects_used_in=skill_info.get('projects', []),
                market_demand=self._get_market_demand(skill_name),
                complementary_skills=self._get_complementary_skills(skill_name)
            )
            
            skills.append(skill)
        
        return skills
    
    def _categorize_skill(self, skill_name: str) -> SkillCategory:
        """Categorize a skill based on its name"""
        skill_lower = skill_name.lower()
        
        for category, skills_list in self.skill_taxonomy.items():
            for skill in skills_list:
                if skill.lower() in skill_lower or skill_lower in skill.lower():
                    return SkillCategory(category)
        
        # Default to creative if can't categorize
        return SkillCategory.CREATIVE
    
    def _get_market_demand(self, skill_name: str) -> float:
        """Get market demand score for a skill"""
        if skill_name in self.skill_demand_data.get("high_demand", []):
            return 0.9
        elif skill_name in self.skill_demand_data.get("medium_demand", []):
            return 0.6
        elif skill_name in self.skill_demand_data.get("low_demand", []):
            return 0.3
        else:
            return 0.5  # Default
    
    def _get_complementary_skills(self, skill_name: str) -> List[str]:
        """Get complementary skills for a given skill"""
        # Simplified complementary skills mapping
        complementary_map = {
            "Video Editing": ["Audio Production", "Graphic Design", "Storytelling"],
            "Photography": ["Photo Editing", "Lighting", "Composition"],
            "Social Media Management": ["Content Creation", "Analytics", "Graphic Design"],
            "Music Production": ["Audio Engineering", "Songwriting", "Sound Design"],
            "Writing": ["SEO", "Research", "Editing"]
        }
        
        return complementary_map.get(skill_name, [])
    
    async def _generate_skill_summary(self, skills: List[Skill]) -> Dict[str, Any]:
        """Generate skill summary statistics"""
        if not skills:
            return {}
        
        # Category distribution
        category_counts = {}
        for skill in skills:
            category = skill.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Level distribution
        level_counts = {}
        for skill in skills:
            level = skill.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Experience statistics
        experiences = [skill.years_experience for skill in skills]
        avg_experience = sum(experiences) / len(experiences)
        
        # Verification statistics
        verified_skills = len([s for s in skills if s.verification_status != SkillVerificationStatus.UNVERIFIED])
        verification_rate = verified_skills / len(skills)
        
        return {
            "total_skills": len(skills),
            "category_distribution": category_counts,
            "level_distribution": level_counts,
            "average_experience": avg_experience,
            "verification_rate": verification_rate,
            "total_endorsements": sum(skill.endorsements for skill in skills),
            "certified_skills": len([s for s in skills if s.certifications])
        }
    
    async def _identify_strengths(self, skills: List[Skill]) -> List[str]:
        """Identify creator's key strengths"""
        strengths = []
        
        # High-level skills
        expert_skills = [s.name for s in skills if s.level in [SkillLevel.EXPERT, SkillLevel.MASTER]]
        if expert_skills:
            strengths.extend([f"Expert-level {skill}" for skill in expert_skills])
        
        # High-demand skills
        high_demand_skills = [s.name for s in skills if s.market_demand > 0.8]
        if high_demand_skills:
            strengths.extend([f"High-demand {skill}" for skill in high_demand_skills])
        
        # Well-endorsed skills
        endorsed_skills = [s.name for s in skills if s.endorsements > 5]
        if endorsed_skills:
            strengths.extend([f"Well-endorsed {skill}" for skill in endorsed_skills])
        
        return strengths[:5]  # Return top 5 strengths
    
    async def _identify_growth_areas(self, skills: List[Skill]) -> List[str]:
        """Identify areas for skill growth"""
        growth_areas = []
        
        # Beginner level skills that could be improved
        beginner_skills = [s.name for s in skills if s.level == SkillLevel.BEGINNER]
        growth_areas.extend([f"Advance {skill} from beginner level" for skill in beginner_skills])
        
        # Skills without recent use
        stale_skills = [s.name for s in skills if (datetime.now() - s.last_used).days > 365]
        growth_areas.extend([f"Refresh {skill} skills" for skill in stale_skills])
        
        # Missing complementary skills
        all_skills = set(s.name for s in skills)
        for skill in skills:
            for comp_skill in skill.complementary_skills:
                if comp_skill not in all_skills:
                    growth_areas.append(f"Learn {comp_skill} to complement {skill.name}")
        
        return growth_areas[:5]  # Return top 5 growth areas
    
    async def _recommend_skills(self, skills: List[Skill], skill_summary: Dict[str, Any]) -> List[str]:
        """Recommend new skills to learn"""
        recommendations = []
        
        # Trending skills in the market
        trending_skills = self.market_trends.get("trending_up", [])
        current_skills = set(s.name for s in skills)
        
        for trending_skill in trending_skills:
            if trending_skill not in current_skills:
                recommendations.append(trending_skill)
        
        # Complementary skills
        for skill in skills:
            for comp_skill in skill.complementary_skills:
                if comp_skill not in current_skills and comp_skill not in recommendations:
                    recommendations.append(comp_skill)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    async def _calculate_skill_score(self, skills: List[Skill]) -> float:
        """Calculate overall skill score"""
        if not skills:
            return 0.0
        
        # Weight skills by level and market demand
        level_weights = {
            SkillLevel.BEGINNER: 0.2,
            SkillLevel.INTERMEDIATE: 0.4,
            SkillLevel.ADVANCED: 0.6,
            SkillLevel.EXPERT: 0.8,
            SkillLevel.MASTER: 1.0
        }
        
        total_score = 0.0
        for skill in skills:
            skill_score = level_weights[skill.level] * skill.market_demand
            # Boost for endorsements and certifications
            skill_score += min(skill.endorsements * 0.01, 0.1)
            skill_score += len(skill.certifications) * 0.05
            total_score += skill_score
        
        return min(total_score / len(skills), 1.0)
    
    async def _calculate_versatility_score(self, skills: List[Skill]) -> float:
        """Calculate versatility score based on skill diversity"""
        if not skills:
            return 0.0
        
        # Count unique categories
        categories = set(skill.category for skill in skills)
        max_categories = len(SkillCategory)
        
        return len(categories) / max_categories
    
    async def _calculate_specialization_score(self, skills: List[Skill]) -> float:
        """Calculate specialization score"""
        if not skills:
            return 0.0
        
        # Find the most common category
        category_counts = {}
        for skill in skills:
            category = skill.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        max_count = max(category_counts.values())
        return max_count / len(skills)
    
    async def _calculate_market_alignment_score(self, skills: List[Skill]) -> float:
        """Calculate how well skills align with market demand"""
        if not skills:
            return 0.0
        
        total_demand = sum(skill.market_demand for skill in skills)
        return total_demand / len(skills)
    
    async def _identify_skill_gaps(self, skill_profile: SkillProfile) -> List[str]:
        """Identify skill gaps based on market trends"""
        current_skills = set(s.name for s in skill_profile.skills)
        high_demand_skills = set(self.skill_demand_data.get("high_demand", []))
        
        return list(high_demand_skills - current_skills)
    
    async def _find_skill_overlaps(self, skill_profile: SkillProfile) -> List[str]:
        """Find overlaps between creator skills and market demands"""
        current_skills = set(s.name for s in skill_profile.skills)
        high_demand_skills = set(self.skill_demand_data.get("high_demand", []))
        
        return list(current_skills.intersection(high_demand_skills))
    
    async def _generate_learning_path(self, skill_profile: SkillProfile, skill_gaps: List[str]) -> List[str]:
        """Generate recommended learning path"""
        learning_path = []
        
        # Prioritize by market demand and complementary skills
        for gap in skill_gaps[:5]:  # Focus on top 5 gaps
            learning_path.append(f"Learn {gap} (high market demand)")
        
        # Add skill improvements
        for skill in skill_profile.skills:
            if skill.level == SkillLevel.BEGINNER:
                learning_path.append(f"Advance {skill.name} to intermediate level")
        
        return learning_path[:10]
    
    async def _identify_market_opportunities(self, skill_profile: SkillProfile) -> List[str]:
        """Identify market opportunities based on skills"""
        opportunities = []
        
        # Match skills with trending opportunities
        for skill in skill_profile.skills:
            if skill.name in self.market_trends.get("trending_up", []):
                opportunities.append(f"Leverage {skill.name} in growing market")
        
        return opportunities
    
    async def _calculate_collaboration_potential(self, skill_profile: SkillProfile) -> Dict[str, float]:
        """Calculate collaboration potential with different creator types"""
        potential = {}
        
        # Simplified collaboration potential calculation
        for category in SkillCategory:
            category_skills = [s for s in skill_profile.skills if s.category == category]
            potential[category.value] = len(category_skills) / len(skill_profile.skills) if skill_profile.skills else 0
        
        return potential
    
    async def _analyze_skill_trends(self, skill_profile: SkillProfile) -> Dict[str, Any]:
        """Analyze skill trends for the creator"""
        trends = {}
        
        for skill in skill_profile.skills:
            if skill.name in self.market_trends.get("trending_up", []):
                trends[skill.name] = "growing"
            elif skill.name in self.market_trends.get("trending_down", []):
                trends[skill.name] = "declining"
            else:
                trends[skill.name] = "stable"
        
        return trends
    
    async def _identify_competitive_advantages(self, skill_profile: SkillProfile) -> List[str]:
        """Identify competitive advantages"""
        advantages = []
        
        # Rare skill combinations
        categories = set(s.category for s in skill_profile.skills)
        if len(categories) >= 4:
            advantages.append("Multi-disciplinary skill set")
        
        # Expert-level skills
        expert_skills = [s for s in skill_profile.skills if s.level in [SkillLevel.EXPERT, SkillLevel.MASTER]]
        if expert_skills:
            advantages.append(f"Expert in {len(expert_skills)} skills")
        
        # High market demand skills
        high_demand_skills = [s for s in skill_profile.skills if s.market_demand > 0.8]
        if high_demand_skills:
            advantages.append(f"Skilled in {len(high_demand_skills)} high-demand areas")
        
        return advantages
    
    async def _calculate_skill_compatibility(self, profile_a: SkillProfile, profile_b: SkillProfile) -> float:
        """Calculate skill compatibility between two creators"""
        skills_a = set(s.name for s in profile_a.skills)
        skills_b = set(s.name for s in profile_b.skills)
        
        # Find complementary skills
        complementary_count = 0
        for skill_a in profile_a.skills:
            for comp_skill in skill_a.complementary_skills:
                if comp_skill in skills_b:
                    complementary_count += 1
        
        # Find overlapping skills (can be good for knowledge sharing)
        overlap_count = len(skills_a.intersection(skills_b))
        
        # Calculate compatibility (balance between complementary and overlap)
        total_skills = len(skills_a.union(skills_b))
        if total_skills == 0:
            return 0.0
        
        compatibility = (complementary_count * 0.7 + overlap_count * 0.3) / total_skills
        return min(compatibility, 1.0)
    
    async def _find_complementary_skills(self, profile_a: SkillProfile, profile_b: SkillProfile) -> List[str]:
        """Find complementary skills between two creators"""
        skills_b_names = set(s.name for s in profile_b.skills)
        complementary = []
        
        for skill_a in profile_a.skills:
            for comp_skill in skill_a.complementary_skills:
                if comp_skill in skills_b_names:
                    complementary.append(f"{skill_a.name} + {comp_skill}")
        
        return complementary
    
    async def _find_overlapping_skills(self, profile_a: SkillProfile, profile_b: SkillProfile) -> List[str]:
        """Find overlapping skills between two creators"""
        skills_a = set(s.name for s in profile_a.skills)
        skills_b = set(s.name for s in profile_b.skills)
        
        return list(skills_a.intersection(skills_b))
    
    async def _identify_collaboration_skill_gaps(self, profile_a: SkillProfile, profile_b: SkillProfile) -> List[str]:
        """Identify skill gaps in collaboration"""
        all_skills = set(s.name for s in profile_a.skills + profile_b.skills)
        high_demand_skills = set(self.skill_demand_data.get("high_demand", []))
        
        return list(high_demand_skills - all_skills)
    
    async def _assess_collaboration_potential(self, profile_a: SkillProfile, profile_b: SkillProfile) -> str:
        """Assess overall collaboration potential"""
        compatibility_score = await self._calculate_skill_compatibility(profile_a, profile_b)
        
        if compatibility_score >= 0.8:
            return "Excellent collaboration potential"
        elif compatibility_score >= 0.6:
            return "Good collaboration potential"
        elif compatibility_score >= 0.4:
            return "Moderate collaboration potential"
        else:
            return "Limited collaboration potential"
    
    async def _recommend_collaboration_roles(self, profile_a: SkillProfile, profile_b: SkillProfile) -> Dict[str, List[str]]:
        """Recommend roles for collaboration"""
        roles = {profile_a.creator_id: [], profile_b.creator_id: []}
        
        # Assign roles based on skill strengths
        for skill in profile_a.skills:
            if skill.level in [SkillLevel.EXPERT, SkillLevel.MASTER]:
                roles[profile_a.creator_id].append(f"Lead {skill.name}")
        
        for skill in profile_b.skills:
            if skill.level in [SkillLevel.EXPERT, SkillLevel.MASTER]:
                roles[profile_b.creator_id].append(f"Lead {skill.name}")
        
        return roles
    
    async def _identify_skill_exchange_opportunities(self, profile_a: SkillProfile, profile_b: SkillProfile) -> List[str]:
        """Identify opportunities for skill exchange"""
        opportunities = []
        
        # Creator A can teach, Creator B can learn
        skills_a = {s.name: s for s in profile_a.skills}
        skills_b = {s.name: s for s in profile_b.skills}
        
        for skill_name, skill in skills_a.items():
            if skill.level in [SkillLevel.ADVANCED, SkillLevel.EXPERT, SkillLevel.MASTER]:
                if skill_name not in skills_b or skills_b[skill_name].level == SkillLevel.BEGINNER:
                    opportunities.append(f"{profile_a.creator_id} can teach {skill_name} to {profile_b.creator_id}")
        
        # Creator B can teach, Creator A can learn
        for skill_name, skill in skills_b.items():
            if skill.level in [SkillLevel.ADVANCED, SkillLevel.EXPERT, SkillLevel.MASTER]:
                if skill_name not in skills_a or skills_a[skill_name].level == SkillLevel.BEGINNER:
                    opportunities.append(f"{profile_b.creator_id} can teach {skill_name} to {profile_a.creator_id}")
        
        return opportunities


# Export main classes
__all__ = [
    'SkillAnalyzer', 'Skill', 'SkillProfile', 'SkillAnalysis', 'SkillMatchingResult',
    'SkillCategory', 'SkillLevel', 'SkillVerificationStatus'
]