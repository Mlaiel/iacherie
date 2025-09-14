"""
Team Formation Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
👥 TEAM FORMATION SERVICE
========================

Advanced AI-powered team formation and optimization service for the Ainflue platform.
Handles intelligent creator matching, team optimization, and collaboration analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Creator type enumeration"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"
    PODCASTER = "podcaster"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    DANCER = "dancer"
    CHEF = "chef"

class SkillLevel(Enum):
    """Skill level enumeration"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5

class TeamRole(Enum):
    """Team role enumeration"""
    LEADER = "leader"
    CREATIVE_DIRECTOR = "creative_director"
    CONTENT_CREATOR = "content_creator"
    EDITOR = "editor"
    MARKETER = "marketer"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"

class MatchingCriteria(Enum):
    """Matching criteria for team formation"""
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    EXPERIENCE_BALANCE = "experience_balance"
    TIMEZONE_COMPATIBILITY = "timezone_compatibility"
    COMMUNICATION_STYLE = "communication_style"
    PROJECT_HISTORY = "project_history"
    AVAILABILITY = "availability"
    BUDGET_ALIGNMENT = "budget_alignment"

@dataclass
class CreatorProfile:
    """Creator profile for team matching"""
    id: str
    name: str
    creator_type: CreatorType
    skills: Dict[str, SkillLevel]
    preferred_roles: List[TeamRole]
    experience_years: int
    timezone: str
    availability_hours: List[int]  # Hours of day available (0-23)
    communication_style: str  # "formal", "casual", "direct", "collaborative"
    languages: List[str]
    portfolio_quality_score: float  # 0.0 - 1.0
    collaboration_rating: float  # 0.0 - 5.0
    completed_projects: int
    preferred_project_types: List[str]
    budget_range: Tuple[float, float]  # Min, Max hourly rate
    location: Optional[str] = None
    personality_traits: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.personality_traits is None:
            self.personality_traits = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ProjectRequirement:
    """Project requirements for team formation"""
    id: str
    title: str
    description: str
    required_skills: Dict[str, SkillLevel]
    required_roles: List[TeamRole]
    team_size: int
    duration_weeks: int
    budget: float
    timezone_preference: Optional[str] = None
    language_requirements: List[str] = None
    project_type: str = ""
    urgency_level: int = 1  # 1-5
    collaboration_style: str = "collaborative"
    created_by: str = ""
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.language_requirements is None:
            self.language_requirements = ["English"]
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class TeamComposition:
    """Recommended team composition"""
    id: str
    project_id: str
    members: List[str]  # Creator IDs
    roles_assignment: Dict[str, TeamRole]  # Creator ID -> Role
    compatibility_score: float  # 0.0 - 1.0
    skill_coverage: Dict[str, float]  # Skill -> Coverage percentage
    estimated_success_probability: float
    team_chemistry_score: float
    cost_estimate: float
    formation_reasoning: List[str]
    potential_risks: List[str]
    recommendations: List[str]
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class FormationMetrics:
    """Team formation service metrics"""
    total_profiles: int = 0
    active_projects: int = 0
    successful_matches: int = 0
    avg_compatibility_score: float = 0.0
    avg_team_size: float = 0.0
    popular_skills: Dict[str, int] = None
    top_creators: List[str] = None
    
    def __post_init__(self) -> None:
        if self.popular_skills is None:
            self.popular_skills = {}
        if self.top_creators is None:
            self.top_creators = []

class TeamFormationService:
    """AI-powered team formation and optimization service"""
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.redis_url = redis_url
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.project_requirements: Dict[str, ProjectRequirement] = {}
        self.team_compositions: Dict[str, TeamComposition] = {}
        self.formation_history: List[Dict[str, Any]] = []
        self.metrics = FormationMetrics()
        self.running = False
        self.redis_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize AI matching weights
        self._init_matching_weights()
    
    async def start(self) -> None:
        """Start the team formation service"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.logger.info("🚀 Team Formation Service started")
            
            # Start background tasks
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._profile_optimizer())
            
        except Exception as e:
            self.logger.error(f"❌ Error starting team formation service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the team formation service"""
        try:
            self.running = False
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("🛑 Team Formation Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping team formation service: {e}")
    
    def _init_matching_weights(self) -> None:
        """Initialize AI matching algorithm weights"""
        self.matching_weights = {
            MatchingCriteria.SKILL_COMPLEMENTARITY: 0.25,
            MatchingCriteria.EXPERIENCE_BALANCE: 0.20,
            MatchingCriteria.TIMEZONE_COMPATIBILITY: 0.15,
            MatchingCriteria.COMMUNICATION_STYLE: 0.15,
            MatchingCriteria.PROJECT_HISTORY: 0.10,
            MatchingCriteria.AVAILABILITY: 0.10,
            MatchingCriteria.BUDGET_ALIGNMENT: 0.05
        }
    
    async def register_creator(
        self,
        name: str,
        creator_type: CreatorType,
        skills: Dict[str, SkillLevel],
        preferred_roles: List[TeamRole],
        experience_years: int,
        timezone: str,
        availability_hours: List[int],
        communication_style: str,
        languages: List[str],
        portfolio_quality_score: float,
        collaboration_rating: float = 0.0,
        completed_projects: int = 0,
        preferred_project_types: Optional[List[str]] = None,
        budget_range: Tuple[float, float] = (50.0, 150.0),
        location: Optional[str] = None,
        personality_traits: Optional[List[str]] = None
    ) -> str:
        """Register a new creator profile"""
        try:
            creator_id = str(uuid.uuid4())
            
            profile = CreatorProfile(
                id=creator_id,
                name=name,
                creator_type=creator_type,
                skills=skills,
                preferred_roles=preferred_roles,
                experience_years=experience_years,
                timezone=timezone,
                availability_hours=availability_hours,
                communication_style=communication_style,
                languages=languages,
                portfolio_quality_score=portfolio_quality_score,
                collaboration_rating=collaboration_rating,
                completed_projects=completed_projects,
                preferred_project_types=preferred_project_types or [],
                budget_range=budget_range,
                location=location,
                personality_traits=personality_traits
            )
            
            self.creator_profiles[creator_id] = profile
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"creator_profile:{creator_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(profile), default=str)
                )
            
            self.logger.info(f"✅ Registered creator {creator_id}: {name}")
            return creator_id
            
        except Exception as e:
            self.logger.error(f"❌ Error registering creator: {e}")
            raise
    
    async def create_project_requirement(
        self,
        title: str,
        description: str,
        required_skills: Dict[str, SkillLevel],
        required_roles: List[TeamRole],
        team_size: int,
        duration_weeks: int,
        budget: float,
        created_by: str,
        timezone_preference: Optional[str] = None,
        language_requirements: Optional[List[str]] = None,
        project_type: str = "",
        urgency_level: int = 1,
        collaboration_style: str = "collaborative"
    ) -> str:
        """Create project requirements for team formation"""
        try:
            project_id = str(uuid.uuid4())
            
            requirement = ProjectRequirement(
                id=project_id,
                title=title,
                description=description,
                required_skills=required_skills,
                required_roles=required_roles,
                team_size=team_size,
                duration_weeks=duration_weeks,
                budget=budget,
                timezone_preference=timezone_preference,
                language_requirements=language_requirements,
                project_type=project_type,
                urgency_level=urgency_level,
                collaboration_style=collaboration_style,
                created_by=created_by
            )
            
            self.project_requirements[project_id] = requirement
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"project_requirement:{project_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(requirement), default=str)
                )
            
            self.logger.info(f"✅ Created project requirement {project_id}: {title}")
            return project_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating project requirement: {e}")
            raise
    
    async def form_optimal_team(
        self,
        project_id: str,
        max_recommendations: int = 3
    ) -> List[TeamComposition]:
        """Form optimal team(s) for a project using AI algorithms"""
        try:
            requirement = self.project_requirements.get(project_id)
            if not requirement:
                raise ValueError(f"Project requirement {project_id} not found")
            
            # Get eligible creators
            eligible_creators = await self._get_eligible_creators(requirement)
            
            if len(eligible_creators) < requirement.team_size:
                self.logger.warning(f"⚠️ Not enough eligible creators for project {project_id}")
                return []
            
            # Generate team combinations
            team_recommendations = []
            
            for _ in range(max_recommendations):
                team_composition = await self._generate_team_composition(
                    requirement, 
                    eligible_creators,
                    exclude_members=[tc.members for tc in team_recommendations]
                )
                
                if team_composition:
                    team_recommendations.append(team_composition)
                    self.team_compositions[team_composition.id] = team_composition
            
            # Sort by compatibility score
            team_recommendations.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            self.logger.info(f"✅ Generated {len(team_recommendations)} team recommendations for project {project_id}")
            return team_recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error forming optimal team: {e}")
            raise
    
    async def _get_eligible_creators(self, requirement: ProjectRequirement) -> List[CreatorProfile]:
        """Get creators eligible for the project"""
        eligible = []
        
        for creator in self.creator_profiles.values():
            # Check basic requirements
            if not self._meets_basic_requirements(creator, requirement):
                continue
            
            # Check skill requirements
            if not self._has_required_skills(creator, requirement):
                continue
            
            # Check availability and timezone
            if not self._is_available(creator, requirement):
                continue
            
            # Check budget alignment
            if not self._budget_compatible(creator, requirement):
                continue
            
            eligible.append(creator)
        
        return eligible
    
    def _meets_basic_requirements(self, creator: CreatorProfile, requirement: ProjectRequirement) -> bool:
        """Check if creator meets basic project requirements"""
        # Language requirements
        if requirement.language_requirements:
            if not any(lang in creator.languages for lang in requirement.language_requirements):
                return False
        
        # Role compatibility
        if requirement.required_roles:
            if not any(role in creator.preferred_roles for role in requirement.required_roles):
                return False
        
        return True
    
    def _has_required_skills(self, creator: CreatorProfile, requirement: ProjectRequirement) -> bool:
        """Check if creator has required skills"""
        for skill, required_level in requirement.required_skills.items():
            creator_level = creator.skills.get(skill)
            if not creator_level or creator_level.value < required_level.value:
                return False
        
        return True
    
    def _is_available(self, creator: CreatorProfile, requirement: ProjectRequirement) -> bool:
        """Check if creator is available for the project"""
        # Simplified availability check
        # In real implementation, check calendar and project commitments
        
        if requirement.timezone_preference:
            # Check timezone compatibility (simplified)
            if creator.timezone != requirement.timezone_preference:
                # Allow ±3 hours timezone difference
                return True  # Simplified for now
        
        return True
    
    def _budget_compatible(self, creator: CreatorProfile, requirement: ProjectRequirement) -> bool:
        """Check if creator's budget is compatible with project"""
        hourly_budget = requirement.budget / (requirement.duration_weeks * 40)  # Assume 40h/week
        
        return creator.budget_range[0] <= hourly_budget <= creator.budget_range[1]
    
    async def _generate_team_composition(
        self,
        requirement: ProjectRequirement,
        eligible_creators: List[CreatorProfile],
        exclude_members: Optional[List[List[str]]] = None
    ) -> Optional[TeamComposition]:
        """Generate a single team composition using AI algorithms"""
        try:
            if exclude_members is None:
                exclude_members = []
            
            # Use genetic algorithm approach for team optimization
            team_members = await self._select_optimal_members(
                requirement, 
                eligible_creators, 
                exclude_members
            )
            
            if len(team_members) < requirement.team_size:
                return None
            
            # Assign roles
            roles_assignment = await self._assign_optimal_roles(team_members, requirement)
            
            # Calculate compatibility scores
            compatibility_score = await self._calculate_compatibility_score(
                team_members, requirement
            )
            
            # Calculate skill coverage
            skill_coverage = await self._calculate_skill_coverage(team_members, requirement)
            
            # Generate insights
            formation_reasoning, potential_risks, recommendations = await self._generate_team_insights(
                team_members, requirement
            )
            
            composition = TeamComposition(
                id=str(uuid.uuid4()),
                project_id=requirement.id,
                members=[member.id for member in team_members],
                roles_assignment=roles_assignment,
                compatibility_score=compatibility_score,
                skill_coverage=skill_coverage,
                estimated_success_probability=min(compatibility_score + 0.1, 1.0),
                team_chemistry_score=compatibility_score * 0.9,
                cost_estimate=self._estimate_team_cost(team_members, requirement),
                formation_reasoning=formation_reasoning,
                potential_risks=potential_risks,
                recommendations=recommendations
            )
            
            return composition
            
        except Exception as e:
            self.logger.error(f"❌ Error generating team composition: {e}")
            return None
    
    async def _select_optimal_members(
        self,
        requirement: ProjectRequirement,
        eligible_creators: List[CreatorProfile],
        exclude_members: List[List[str]]
    ) -> List[CreatorProfile]:
        """Select optimal team members using AI algorithms"""
        # Simplified selection algorithm
        # In real implementation, use more sophisticated AI/ML algorithms
        
        # Score each creator
        creator_scores = {}
        for creator in eligible_creators:
            if any(creator.id in excluded for excluded in exclude_members):
                continue
            
            score = 0.0
            
            # Skill alignment score
            for skill, required_level in requirement.required_skills.items():
                creator_level = creator.skills.get(skill, SkillLevel.BEGINNER)
                if creator_level.value >= required_level.value:
                    score += creator_level.value * 0.2
            
            # Experience score
            experience_score = min(creator.experience_years / 10, 1.0)
            score += experience_score * 0.3
            
            # Collaboration rating
            score += creator.collaboration_rating / 5.0 * 0.2
            
            # Portfolio quality
            score += creator.portfolio_quality_score * 0.2
            
            # Project history bonus
            if creator.completed_projects > 0:
                score += min(creator.completed_projects / 20, 0.1)
            
            creator_scores[creator] = score
        
        # Select top creators
        sorted_creators = sorted(creator_scores.items(), key=lambda x: x[1], reverse=True)
        selected = [creator for creator, score in sorted_creators[:requirement.team_size]]
        
        return selected
    
    async def _assign_optimal_roles(
        self,
        team_members: List[CreatorProfile],
        requirement: ProjectRequirement
    ) -> Dict[str, TeamRole]:
        """Assign optimal roles to team members"""
        roles_assignment = {}
        available_roles = requirement.required_roles.copy()
        
        # Assign roles based on preferences and skills
        for member in team_members:
            best_role = None
            best_score = 0.0
            
            for role in available_roles:
                if role in member.preferred_roles:
                    # Calculate role fit score
                    score = 1.0  # Base score for preference
                    
                    # Add experience bonus
                    if member.experience_years > 5:
                        score += 0.2
                    
                    # Add collaboration rating bonus
                    score += member.collaboration_rating / 5.0 * 0.3
                    
                    if score > best_score:
                        best_score = score
                        best_role = role
            
            if best_role:
                roles_assignment[member.id] = best_role
                available_roles.remove(best_role)
            elif available_roles:
                # Assign any remaining role
                roles_assignment[member.id] = available_roles.pop(0)
        
        return roles_assignment
    
    async def _calculate_compatibility_score(
        self,
        team_members: List[CreatorProfile],
        requirement: ProjectRequirement
    ) -> float:
        """Calculate team compatibility score"""
        score = 0.0
        
        # Skill complementarity
        skill_scores = []
        for skill, required_level in requirement.required_skills.items():
            team_skill_levels = [
                member.skills.get(skill, SkillLevel.BEGINNER).value 
                for member in team_members
            ]
            avg_skill = sum(team_skill_levels) / len(team_skill_levels)
            skill_coverage = min(avg_skill / required_level.value, 1.0)
            skill_scores.append(skill_coverage)
        
        skill_compatibility = sum(skill_scores) / len(skill_scores) if skill_scores else 0.0
        score += skill_compatibility * self.matching_weights[MatchingCriteria.SKILL_COMPLEMENTARITY]
        
        # Experience balance
        experience_levels = [member.experience_years for member in team_members]
        experience_variance = np.var(experience_levels)
        experience_balance = max(0, 1.0 - experience_variance / 100)  # Normalize variance
        score += experience_balance * self.matching_weights[MatchingCriteria.EXPERIENCE_BALANCE]
        
        # Communication style compatibility
        communication_styles = [member.communication_style for member in team_members]
        style_compatibility = len(set(communication_styles)) / len(communication_styles)
        style_compatibility = 1.0 - style_compatibility + 0.1  # Prefer similar styles
        score += style_compatibility * self.matching_weights[MatchingCriteria.COMMUNICATION_STYLE]
        
        # Project history compatibility
        avg_projects = sum(member.completed_projects for member in team_members) / len(team_members)
        project_history_score = min(avg_projects / 10, 1.0)
        score += project_history_score * self.matching_weights[MatchingCriteria.PROJECT_HISTORY]
        
        # Additional compatibility factors
        score += 0.1  # Base compatibility bonus
        
        return min(score, 1.0)
    
    async def _calculate_skill_coverage(
        self,
        team_members: List[CreatorProfile],
        requirement: ProjectRequirement
    ) -> Dict[str, float]:
        """Calculate skill coverage for the team"""
        coverage = {}
        
        for skill, required_level in requirement.required_skills.items():
            team_skill_levels = [
                member.skills.get(skill, SkillLevel.BEGINNER).value 
                for member in team_members
            ]
            max_skill_level = max(team_skill_levels)
            coverage_percentage = min(max_skill_level / required_level.value, 1.0)
            coverage[skill] = coverage_percentage
        
        return coverage
    
    def _estimate_team_cost(
        self,
        team_members: List[CreatorProfile],
        requirement: ProjectRequirement
    ) -> float:
        """Estimate total team cost"""
        total_cost = 0.0
        hours_per_week = 40  # Assume full-time
        total_hours = requirement.duration_weeks * hours_per_week
        
        for member in team_members:
            # Use average of budget range
            hourly_rate = (member.budget_range[0] + member.budget_range[1]) / 2
            member_cost = hourly_rate * (total_hours / len(team_members))
            total_cost += member_cost
        
        return total_cost
    
    async def _generate_team_insights(
        self,
        team_members: List[CreatorProfile],
        requirement: ProjectRequirement
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate team formation insights and recommendations"""
        reasoning = []
        risks = []
        recommendations = []
        
        # Formation reasoning
        avg_experience = sum(m.experience_years for m in team_members) / len(team_members)
        reasoning.append(f"Team has average {avg_experience:.1f} years of experience")
        
        skill_strengths = []
        for skill, required_level in requirement.required_skills.items():
            team_max_skill = max(
                m.skills.get(skill, SkillLevel.BEGINNER).value 
                for m in team_members
            )
            if team_max_skill >= required_level.value:
                skill_strengths.append(skill)
        
        if skill_strengths:
            reasoning.append(f"Strong coverage in: {', '.join(skill_strengths)}")
        
        # Potential risks
        if avg_experience < 2:
            risks.append("Team may lack sufficient experience for complex tasks")
        
        if len(set(m.timezone for m in team_members)) > 2:
            risks.append("Multiple timezones may complicate coordination")
        
        # Recommendations
        if avg_experience < 3:
            recommendations.append("Consider adding a senior mentor to guide the team")
        
        recommendations.append("Establish clear communication protocols and regular check-ins")
        
        return reasoning, risks, recommendations
    
    async def get_team_recommendation(self, composition_id: str) -> Optional[Dict[str, Any]]:
        """Get team composition recommendation"""
        try:
            composition = self.team_compositions.get(composition_id)
            if composition:
                return asdict(composition)
            
            # Try Redis cache
            if self.redis_client:
                cached = await self.redis_client.get(f"team_composition:{composition_id}")
                if cached:
                    return json.loads(cached)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting team recommendation: {e}")
            return None
    
    async def _metrics_collector(self) -> None:
        """Collect team formation metrics"""
        while self.running:
            try:
                # Update metrics
                self.metrics.total_profiles = len(self.creator_profiles)
                self.metrics.active_projects = len(self.project_requirements)
                self.metrics.successful_matches = len(self.team_compositions)
                
                if self.team_compositions:
                    avg_score = sum(tc.compatibility_score for tc in self.team_compositions.values())
                    self.metrics.avg_compatibility_score = avg_score / len(self.team_compositions)
                    
                    avg_size = sum(len(tc.members) for tc in self.team_compositions.values())
                    self.metrics.avg_team_size = avg_size / len(self.team_compositions)
                
                # Popular skills
                skill_counts = defaultdict(int)
                for creator in self.creator_profiles.values():
                    for skill in creator.skills.keys():
                        skill_counts[skill] += 1
                
                self.metrics.popular_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10])
                
                # Store in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        "team_formation:metrics",
                        300,  # 5 minutes
                        json.dumps(asdict(self.metrics), default=str)
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _profile_optimizer(self) -> None:
        """Optimize creator profiles based on successful matches"""
        while self.running:
            try:
                # Analyze successful team formations
                # Update creator compatibility scores
                # Suggest profile improvements
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in profile optimizer: {e}")
                await asyncio.sleep(300)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get team formation metrics"""
        return asdict(self.metrics)
    
    async def get_creator_recommendations(self, creator_id: str) -> Dict[str, Any]:
        """Get improvement recommendations for a creator"""
        try:
            creator = self.creator_profiles.get(creator_id)
            if not creator:
                return {"error": "Creator not found"}
            
            recommendations = []
            
            # Skill recommendations
            popular_skills = list(self.metrics.popular_skills.keys())[:5]
            missing_popular = [skill for skill in popular_skills if skill not in creator.skills]
            if missing_popular:
                recommendations.append(f"Consider learning these in-demand skills: {', '.join(missing_popular[:3])}")
            
            # Experience recommendations
            if creator.experience_years < 2:
                recommendations.append("Building more project experience will improve team matching opportunities")
            
            # Portfolio recommendations
            if creator.portfolio_quality_score < 0.7:
                recommendations.append("Improving portfolio quality will increase selection chances")
            
            return {
                "creator_id": creator_id,
                "recommendations": recommendations,
                "current_score": creator.collaboration_rating,
                "match_potential": len([p for p in self.project_requirements.values() if self._meets_basic_requirements(creator, p)])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting creator recommendations: {e}")
            return {"error": str(e)}


# Example usage and testing
async def main() -> None:
    """Test the team formation service"""
    service = TeamFormationService()
    
    try:
        await service.start()
        
        # Register some creators
        musician_id = await service.register_creator(
            "Alice Music",
            CreatorType.MUSICIAN,
            {"music_production": SkillLevel.EXPERT, "audio_editing": SkillLevel.ADVANCED},
            [TeamRole.CREATIVE_DIRECTOR, TeamRole.CONTENT_CREATOR],
            5,
            "UTC",
            list(range(9, 17)),  # 9 AM - 5 PM
            "collaborative",
            ["English", "Spanish"],
            0.9,
            4.5,
            15,
            ["music", "podcasts"],
            (75.0, 120.0)
        )
        
        photographer_id = await service.register_creator(
            "Bob Photo",
            CreatorType.PHOTOGRAPHER,
            {"photography": SkillLevel.EXPERT, "photo_editing": SkillLevel.ADVANCED},
            [TeamRole.CONTENT_CREATOR, TeamRole.SPECIALIST],
            3,
            "UTC",
            list(range(8, 16)),
            "direct",
            ["English"],
            0.85,
            4.2,
            10,
            ["visual", "marketing"],
            (60.0, 100.0)
        )
        
        # Create a project requirement
        project_id = await service.create_project_requirement(
            "Music Video Production",
            "Create a professional music video with high-quality visuals",
            {
                "music_production": SkillLevel.ADVANCED,
                "photography": SkillLevel.ADVANCED,
                "video_editing": SkillLevel.INTERMEDIATE
            },
            [TeamRole.CREATIVE_DIRECTOR, TeamRole.CONTENT_CREATOR],
            2,
            4,
            8000.0,
            "project_manager_123",
            "UTC",
            ["English"],
            "music_video",
            3
        )
        
        # Form optimal team
        team_recommendations = await service.form_optimal_team(project_id, max_recommendations=2)
        
        print(f"Generated {len(team_recommendations)} team recommendations")
        for i, team in enumerate(team_recommendations):
            print(f"Team {i+1}: Compatibility {team.compatibility_score:.2f}, Cost ${team.cost_estimate:.2f}")
        
        # Get metrics
        metrics = await service.get_metrics()
        print(f"Service Metrics: {metrics}")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())