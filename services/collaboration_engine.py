"""Collaboration Engine
Creator matching and collaboration management system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class CollaborationStatus(Enum):
    """
Collaboration status"""

    PROPOSED = "proposed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class CreatorProfile:
    """Creator profile for matching"""
    user_id: str
    username: str
    creator_type: str
    genres: List[str]
    skills: List[str]
    experience_level: str
    average_engagement: float
    follower_count: int
    collaboration_history: int
    rating: float
    availability: bool
    preferred_collaboration_types: List[str]
    location: Optional[str] = None


@dataclass
class CollaborationProposal:
    """
Collaboration proposal structure"""
    id: str
    proposer_id: str
    target_id: str
    collaboration_type: str
    project_description: str
    proposed_revenue_split: Dict[str, float]
    timeline: int  # days
    requirements: List[str]
    status: CollaborationStatus
    created_at: datetime
    expires_at: datetime
    metadata: Optional[Dict] = None


@dataclass
class CompatibilityScore:
    """
Creator compatibility scoring"""
    total_score: float
    genre_match: float
    skill_complement: float
    experience_balance: float
    engagement_compatibility: float
    collaboration_history: float
    factors: Dict[str, Any]


class CollaborationEngine:
    """
Advanced creator collaboration and matching system"""
    
    def __init__(self) -> None:
        self.creator_profiles = {}
        self.collaborations = {}
        self.matching_history = {}
        
    async def register_creator_profile(
        self,
        user_id: str,
        username: str,
        creator_data: Dict[str, Any]
    ) -> CreatorProfile:
        """
Register or update creator profile for collaboration matching"""
        try:
            profile = CreatorProfile(
                user_id=user_id,
                username=username,
                creator_type=creator_data.get("creator_type", "musician"),
                genres=creator_data.get("genres", []),
                skills=creator_data.get("skills", []),
                experience_level=creator_data.get("experience_level", "beginner"),
                average_engagement=creator_data.get("average_engagement", 0.0),
                follower_count=creator_data.get("follower_count", 0),
                collaboration_history=creator_data.get("collaboration_history", 0),
                rating=creator_data.get("rating", 5.0),
                availability=creator_data.get("availability", True),
                preferred_collaboration_types=creator_data.get("preferred_collaboration_types", []),
                location=creator_data.get("location")
            )
            
            self.creator_profiles[user_id] = profile
            
            logger.info(f"Creator profile registered: {username} ({user_id})")
            return profile
            
        except Exception as e:
            logger.error(f"Error registering creator profile: {str(e)}")
            raise
    
    async def find_collaboration_matches(
        self,
        creator_id: str,
        collaboration_type: str,
        preferences: Optional[Dict] = None
    ) -> List[Tuple[CreatorProfile, CompatibilityScore]]:
        """Find potential collaboration matches for a creator"""
        try:
            requesting_creator = self.creator_profiles.get(creator_id)
            if not requesting_creator:
                return []
            
            preferences = preferences or {}
            matches = []
            
            for other_id, other_creator in self.creator_profiles.items():
                if other_id == creator_id or not other_creator.availability:
                    continue
                
                # Check if collaboration type is preferred
                if (collaboration_type not in other_creator.preferred_collaboration_types and
                    other_creator.preferred_collaboration_types):
                    continue
                
                # Apply preference filters
                if self._apply_preference_filters(other_creator, preferences):
                    compatibility = await self._calculate_compatibility(
                        requesting_creator,
                        other_creator,
                        collaboration_type
                    )
                    
                    if compatibility.total_score >= 0.6:  # Minimum compatibility threshold
                        matches.append((other_creator, compatibility))
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x[1].total_score, reverse=True)
            
            logger.info(f"Found {len(matches)} collaboration matches for {creator_id}")
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Error finding collaboration matches: {str(e)}")
            return []
    
    async def create_collaboration_proposal(
        self,
        proposer_id: str,
        target_id: str,
        collaboration_data: Dict[str, Any]
    ) -> CollaborationProposal:
        """Create a collaboration proposal"""
        try:
            proposal_id = str(uuid.uuid4())
            
            # Validate revenue split
            revenue_split = collaboration_data.get("revenue_split", {})
            if abs(sum(revenue_split.values()) - 1.0) > 0.01:
                raise ValueError("Revenue split must sum to 100%")
            
            proposal = CollaborationProposal(
                id=proposal_id,
                proposer_id=proposer_id,
                target_id=target_id,
                collaboration_type=collaboration_data.get("type", "feature"),
                project_description=collaboration_data.get("description", ""),
                proposed_revenue_split=revenue_split,
                timeline=collaboration_data.get("timeline_days", 30),
                requirements=collaboration_data.get("requirements", []),
                status=CollaborationStatus.PROPOSED,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),  # 7 day expiry
                metadata=collaboration_data.get("metadata", {})
            )
            
            self.collaborations[proposal_id] = proposal
            
            # Generate contract terms automatically
            await self._generate_collaboration_contract(proposal)
            
            logger.info(f"Collaboration proposal created: {proposal_id}")
            return proposal
            
        except Exception as e:
            logger.error(f"Error creating collaboration proposal: {str(e)}")
            raise
    
    async def respond_to_proposal(
        self,
        proposal_id: str,
        target_user_id: str,
        response: str,  # accept, reject, counter
        counter_terms: Optional[Dict] = None
    ) -> bool:
        """Respond to a collaboration proposal"""
        try:
            proposal = self.collaborations.get(proposal_id)
            if not proposal:
                return False
                
            if proposal.target_id != target_user_id:
                return False
                
            if response == "accept":
                proposal.status = CollaborationStatus.ACCEPTED
                
                # Create project workspace
                await self._create_collaboration_workspace(proposal)
                
            elif response == "reject":
                proposal.status = CollaborationStatus.CANCELLED
                
            elif response == "counter" and counter_terms:
                # Update proposal with counter terms
                if "revenue_split" in counter_terms:
                    proposal.proposed_revenue_split = counter_terms["revenue_split"]
                if "timeline" in counter_terms:
                    proposal.timeline = counter_terms["timeline"]
                if "requirements" in counter_terms:
                    proposal.requirements = counter_terms["requirements"]
                
                proposal.status = CollaborationStatus.PENDING
                proposal.expires_at = datetime.now() + timedelta(days=3)  # 3 day counter expiry
            
            logger.info(f"Proposal {proposal_id} response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error responding to proposal: {str(e)}")
            return False
    
    async def manage_collaboration_workflow(
        self,
        collaboration_id: str,
        action: str,
        user_id: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Manage collaboration workflow and milestones"""
        try:
            collaboration = self.collaborations.get(collaboration_id)
            if not collaboration:
                return {"error": "Collaboration not found"}
            
            # Verify user is part of collaboration
            if user_id not in [collaboration.proposer_id, collaboration.target_id]:
                return {"error": "Unauthorized"}
            
            result = {"success": True, "action": action}
            
            if action == "start_project":
                collaboration.status = CollaborationStatus.IN_PROGRESS
                result["project_started"] = True
                
            elif action == "submit_deliverable":
                deliverable_data = data or {}
                # Store deliverable information
                if "deliverables" not in collaboration.metadata:
                    collaboration.metadata["deliverables"] = []
                
                collaboration.metadata["deliverables"].append({
                    "user_id": user_id,
                    "type": deliverable_data.get("type", "audio"),
                    "file_path": deliverable_data.get("file_path"),
                    "description": deliverable_data.get("description"),
                    "submitted_at": datetime.now().isoformat()
                })
                
                result["deliverable_submitted"] = True
                
            elif action == "approve_deliverable":
                # Mark deliverable as approved
                deliverable_id = data.get("deliverable_id")
                if deliverable_id is not None and "deliverables" in collaboration.metadata:
                    if deliverable_id < len(collaboration.metadata["deliverables"]):
                        collaboration.metadata["deliverables"][deliverable_id]["approved"] = True
                        collaboration.metadata["deliverables"][deliverable_id]["approved_by"] = user_id
                        collaboration.metadata["deliverables"][deliverable_id]["approved_at"] = datetime.now().isoformat()
                
                result["deliverable_approved"] = True
                
            elif action == "complete_project":
                collaboration.status = CollaborationStatus.COMPLETED
                
                # Calculate final revenue distribution
                await self._finalize_collaboration_revenue(collaboration)
                
                result["project_completed"] = True
                
            elif action == "dispute":
                collaboration.status = CollaborationStatus.DISPUTED
                result["dispute_raised"] = True
                
                # Initiate dispute resolution process
                await self._initiate_dispute_resolution(collaboration, user_id, data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error managing collaboration workflow: {str(e)}")
            return {"error": str(e)}
    
    async def generate_collaboration_insights(
        self,
        creator_id: str
    ) -> Dict[str, Any]:
        """Generate insights about collaboration opportunities and performance"""
        try:
            creator = self.creator_profiles.get(creator_id)
            if not creator:
                return {"error": "Creator not found"}
            
            # Analyze collaboration history
            creator_collaborations = [
                c for c in self.collaborations.values()
                if creator_id in [c.proposer_id, c.target_id]
            ]
            
            completed_collaborations = [
                c for c in creator_collaborations
                if c.status == CollaborationStatus.COMPLETED
            ]
            
            # Calculate success metrics
            success_rate = len(completed_collaborations) / len(creator_collaborations) if creator_collaborations else 0
            
            # Analyze collaboration types
            collaboration_types = {}
            for collab in completed_collaborations:
                collab_type = collab.collaboration_type
                if collab_type not in collaboration_types:
                    collaboration_types[collab_type] = 0
                collaboration_types[collab_type] += 1
            
            most_successful_type = max(collaboration_types.items(), key=lambda x: x[1])[0] if collaboration_types else None
            
            # Generate recommendations
            recommendations = await self._generate_collaboration_recommendations(creator, creator_collaborations)
            
            # Calculate networking score
            networking_score = self._calculate_networking_score(creator, creator_collaborations)
            
            insights = {
                "creator_id": creator_id,
                "collaboration_stats": {
                    "total_collaborations": len(creator_collaborations),
                    "completed_collaborations": len(completed_collaborations),
                    "success_rate": success_rate,
                    "most_successful_type": most_successful_type,
                    "collaboration_types": collaboration_types
                },
                "networking_score": networking_score,
                "recommendations": recommendations,
                "potential_matches": len(await self.find_collaboration_matches(creator_id, "any")),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating collaboration insights: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_type: str
    ) -> CompatibilityScore:
        """Calculate compatibility score between two creators"""
        try:
            scores = {}
            
            # Genre compatibility (25%)
            genre_overlap = len(set(creator1.genres) & set(creator2.genres))
            genre_total = len(set(creator1.genres) | set(creator2.genres))
            genre_score = (genre_overlap / genre_total) if genre_total > 0 else 0
            scores["genre_match"] = genre_score * 0.25
            
            # Skill complementarity (20%)
            skill_complement = len(set(creator1.skills) - set(creator2.skills)) / max(len(creator1.skills), 1)
            scores["skill_complement"] = min(skill_complement, 1.0) * 0.20
            
            # Experience balance (15%)
            exp_levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
            exp1 = exp_levels.get(creator1.experience_level, 1)
            exp2 = exp_levels.get(creator2.experience_level, 1)
            exp_balance = 1 - abs(exp1 - exp2) / 3  # Normalize to 0-1
            scores["experience_balance"] = exp_balance * 0.15
            
            # Engagement compatibility (20%)
            eng_ratio = min(creator1.average_engagement, creator2.average_engagement) / max(creator1.average_engagement, creator2.average_engagement, 0.001)
            scores["engagement_compatibility"] = eng_ratio * 0.20
            
            # Collaboration history factor (20%)
            history_score = min((creator1.collaboration_history + creator2.collaboration_history) / 10, 1.0)
            scores["collaboration_history"] = history_score * 0.20
            
            total_score = sum(scores.values())
            
            return CompatibilityScore(
                total_score=total_score,
                genre_match=scores["genre_match"],
                skill_complement=scores["skill_complement"],
                experience_balance=scores["experience_balance"],
                engagement_compatibility=scores["engagement_compatibility"],
                collaboration_history=scores["collaboration_history"],
                factors={
                    "genre_overlap": genre_overlap,
                    "complementary_skills": list(set(creator1.skills) - set(creator2.skills)),
                    "common_skills": list(set(creator1.skills) & set(creator2.skills))
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {str(e)}")
            return CompatibilityScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {})
    
    def _apply_preference_filters(
        self,
        creator: CreatorProfile,
        preferences: Dict
    ) -> bool:
        """Apply preference filters to creator matching"""
        try:
            # Genre filter
            if "genres" in preferences:
                required_genres = preferences["genres"]
                if not any(genre in creator.genres for genre in required_genres):
                    return False
            
            # Experience level filter
            if "min_experience" in preferences:
                exp_levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                creator_exp = exp_levels.get(creator.experience_level, 1)
                min_exp = exp_levels.get(preferences["min_experience"], 1)
                if creator_exp < min_exp:
                    return False
            
            # Follower count filter
            if "min_followers" in preferences:
                if creator.follower_count < preferences["min_followers"]:
                    return False
            
            # Rating filter
            if "min_rating" in preferences:
                if creator.rating < preferences["min_rating"]:
                    return False
            
            # Location filter
            if "location" in preferences and creator.location:
                if preferences["location"].lower() not in creator.location.lower():
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying preference filters: {str(e)}")
            return False
    
    async def _generate_collaboration_contract(self, proposal -> None: CollaborationProposal) -> None:
        """Generate automatic collaboration contract terms"""
        try:
            contract_terms = {
                "proposal_id": proposal.id,
                "parties": {
                    "proposer": proposal.proposer_id,
                    "collaborator": proposal.target_id
                },
                "project_scope": proposal.project_description,
                "timeline": f"{proposal.timeline} days",
                "revenue_distribution": proposal.proposed_revenue_split,
                "intellectual_property": "Shared ownership based on contribution",
                "dispute_resolution": "Platform mediation followed by arbitration",
                "termination_clause": "Either party may terminate with 7 days notice",
                "generated_at": datetime.now().isoformat()
            }
            
            proposal.metadata["contract_terms"] = contract_terms
            
        except Exception as e:
            logger.error(f"Error generating collaboration contract: {str(e)}")
    
    async def _create_collaboration_workspace(self, proposal -> None: CollaborationProposal) -> None:
        """Create collaborative workspace for accepted proposal"""
        try:
            workspace = {
                "collaboration_id": proposal.id,
                "workspace_url": f"/workspace/{proposal.id}",
                "shared_files": [],
                "communication_channel": f"collab-{proposal.id}",
                "milestones": self._generate_project_milestones(proposal),
                "created_at": datetime.now().isoformat()
            }
            
            proposal.metadata["workspace"] = workspace
            
        except Exception as e:
            logger.error(f"Error creating collaboration workspace: {str(e)}")
    
    def _generate_project_milestones(self, proposal: CollaborationProposal) -> List[Dict]:
        """Generate project milestones based on collaboration type"""
        try:
            milestones = []
            
            if proposal.collaboration_type == "feature":
                milestones = [
                    {"name": "Initial Recording", "deadline_days": proposal.timeline * 0.3},
                    {"name": "Review and Feedback", "deadline_days": proposal.timeline * 0.6},
                    {"name": "Final Mix", "deadline_days": proposal.timeline * 0.9},
                    {"name": "Release Ready", "deadline_days": proposal.timeline}
                ]
            elif proposal.collaboration_type == "remix":
                milestones = [
                    {"name": "Remix Concept", "deadline_days": proposal.timeline * 0.2},
                    {"name": "First Draft", "deadline_days": proposal.timeline * 0.5},
                    {"name": "Refined Version", "deadline_days": proposal.timeline * 0.8},
                    {"name": "Final Master", "deadline_days": proposal.timeline}
                ]
            else:
                # Default milestones
                milestones = [
                    {"name": "Project Kickoff", "deadline_days": proposal.timeline * 0.1},
                    {"name": "Mid-point Review", "deadline_days": proposal.timeline * 0.5},
                    {"name": "Final Delivery", "deadline_days": proposal.timeline}
                ]
            
            # Add actual dates
            for milestone in milestones:
                deadline = proposal.created_at + timedelta(days=milestone["deadline_days"])
                milestone["deadline_date"] = deadline.isoformat()
                milestone["completed"] = False
            
            return milestones
            
        except Exception as e:
            logger.error(f"Error generating project milestones: {str(e)}")
            return []
    
    async def _finalize_collaboration_revenue(self, collaboration -> None: CollaborationProposal) -> None:
        """Finalize revenue distribution for completed collaboration"""
        try:
            # This would integrate with the revenue distribution engine
            # For now, just record the completion
            collaboration.metadata["revenue_finalized"] = True
            collaboration.metadata["finalized_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error finalizing collaboration revenue: {str(e)}")
    
    async def _initiate_dispute_resolution(
        self,
        collaboration -> None: CollaborationProposal,
        disputing_user -> None: str,
        dispute_data -> None: Dict
    ) -> None:
        """Initiate dispute resolution process"""
        try:
            dispute_record = {
                "disputing_user": disputing_user,
                "dispute_reason": dispute_data.get("reason", ""),
                "dispute_details": dispute_data.get("details", ""),
                "initiated_at": datetime.now().isoformat(),
                "status": "open",
                "resolution": None
            }
            
            collaboration.metadata["dispute"] = dispute_record
            
        except Exception as e:
            logger.error(f"Error initiating dispute resolution: {str(e)}")
    
    async def _generate_collaboration_recommendations(
        self,
        creator: CreatorProfile,
        collaboration_history: List[CollaborationProposal]
    ) -> List[str]:
        """Generate collaboration recommendations for creator"""
        try:
            recommendations = []
            
            if len(collaboration_history) == 0:
                recommendations.extend([
                    "Start with simple feature collaborations to build experience",
                    "Focus on creators with complementary skills",
                    "Clearly define project scope and expectations"
                ])
            elif len(collaboration_history) < 3:
                recommendations.extend([
                    "Continue building collaboration portfolio",
                    "Try different types of collaborations",
                    "Request feedback from previous collaborators"
                ])
            else:
                # Analyze patterns for experienced collaborators
                success_rate = len([c for c in collaboration_history if c.status == CollaborationStatus.COMPLETED]) / len(collaboration_history)
                
                if success_rate < 0.7:
                    recommendations.extend([
                        "Review project scoping and timeline estimation",
                        "Improve communication during collaborations",
                        "Consider working with more experienced partners"
                    ])
                else:
                    recommendations.extend([
                        "Consider mentoring newer creators",
                        "Explore more complex collaboration types",
                        "Build long-term creative partnerships"
                    ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating collaboration recommendations: {str(e)}")
            return ["Continue exploring collaboration opportunities"]
    
    def _calculate_networking_score(
        self,
        creator: CreatorProfile,
        collaboration_history: List[CollaborationProposal]
    ) -> float:
        """Calculate networking score for creator"""
        try:
            # Base score from collaboration count
            collab_score = min(len(collaboration_history) / 10, 1.0) * 40
            
            # Success rate factor
            if collaboration_history:
                success_rate = len([c for c in collaboration_history if c.status == CollaborationStatus.COMPLETED]) / len(collaboration_history)
                success_score = success_rate * 30
            else:
                success_score = 0
            
            # Diversity factor (different collaboration types)
            types = set(c.collaboration_type for c in collaboration_history)
            diversity_score = min(len(types) / 3, 1.0) * 20
            
            # Rating factor
            rating_score = (creator.rating / 5.0) * 10
            
            total_score = collab_score + success_score + diversity_score + rating_score
            
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"Error calculating networking score: {str(e)}")
            return 0.0