"""Community Building Workflow

AI-powered community building and social engagement workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class CommunityRole(Enum):
    """Community roles"""
    MEMBER = "member"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    AMBASSADOR = "ambassador"
    LEADER = "leader"


class CommunityEventType(Enum):
    """Types of community events"""
    WELCOME_NEW_MEMBER = "welcome_new_member"
    MILESTONE_CELEBRATION = "milestone_celebration"
    COLLABORATION_FORMED = "collaboration_formed"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    MENTORSHIP_MATCH = "mentorship_match"
    GROUP_CHALLENGE = "group_challenge"


@dataclass
class CommunityMember:
    """Community member profile"""
    user_id: str
    username: str
    role: CommunityRole
    join_date: datetime
    contribution_score: float = 0.0
    reputation_points: int = 0
    specialties: List[str] = field(default_factory=list)
    mentoring_capacity: int = 0
    is_active: bool = True


@dataclass
class CommunityEvent:
    """Community event"""
    event_id: str
    event_type: CommunityEventType
    title: str
    description: str
    participants: List[str]
    organizer_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    engagement_metrics: Dict[str, int] = field(default_factory=dict)


class CommunityBuildingWorkflow:
    """AI-powered community building workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.community_members: Dict[str, CommunityMember] = {}
        self.community_events: Dict[str, CommunityEvent] = {}
        self.mentorship_pairs: Dict[str, str] = {}  # mentor_id -> mentee_id
        
    async def onboard_new_member(
        self,
        user_id: str,
        username: str,
        user_interests: List[str],
        experience_level: str = "beginner"
    ) -> CommunityMember:
        """
        Onboard new community member
        
        Args:
            user_id: User identifier
            username: User's display name
            user_interests: User's areas of interest
            experience_level: User's experience level
            
        Returns:
            CommunityMember object
        """
        try:
            # Create community member profile
            member = CommunityMember(
                user_id=user_id,
                username=username,
                role=CommunityRole.MEMBER,
                join_date=datetime.utcnow(),
                specialties=user_interests
            )
            
            # Store member
            self.community_members[user_id] = member
            
            # Create welcome event
            await self._create_welcome_event(member)
            
            # Suggest potential connections
            connections = await self._suggest_connections(member)
            
            # Assign mentor if beginner
            if experience_level == "beginner":
                mentor = await self._find_suitable_mentor(member)
                if mentor:
                    await self._create_mentorship_pair(mentor.user_id, user_id)
            
            # Record metrics
            await self.metrics_collector.record_metric("community_members_joined", 1)
            
            logger.info(f"New member onboarded: {username} ({user_id})")
            return member
            
        except Exception as e:
            logger.error(f"Member onboarding failed: {e}")
            raise WorkflowError(f"Member onboarding failed: {e}")
    
    async def update_contribution_score(
        self,
        user_id: str,
        activity_type: str,
        impact_score: float,
        activity_data: Dict[str, Any] = None
    ) -> float:
        """
        Update member's contribution score based on community activities
        
        Args:
            user_id: User identifier
            activity_type: Type of community activity
            impact_score: Impact score of the activity
            activity_data: Additional activity data
            
        Returns:
            Updated contribution score
        """
        try:
            if user_id not in self.community_members:
                return 0.0
            
            member = self.community_members[user_id]
            
            # Calculate contribution points based on activity type
            activity_multipliers = {
                "helpful_response": 2.0,
                "knowledge_share": 3.0,
                "mentoring_session": 4.0,
                "content_creation": 1.5,
                "collaboration_initiation": 2.5,
                "event_participation": 1.0,
                "community_moderation": 3.5
            }
            
            multiplier = activity_multipliers.get(activity_type, 1.0)
            points_earned = impact_score * multiplier
            
            # Update scores
            member.contribution_score += points_earned
            member.reputation_points += int(points_earned * 10)
            
            # Check for role promotion
            await self._check_role_promotion(member)
            
            # Record metrics
            await self.metrics_collector.record_metric("community_contribution_points", points_earned)
            
            logger.info(f"Contribution score updated for {user_id}: +{points_earned:.2f}")
            return member.contribution_score
            
        except Exception as e:
            logger.error(f"Contribution score update failed: {e}")
            return 0.0
    
    async def facilitate_collaboration(
        self,
        initiator_id: str,
        target_user_ids: List[str],
        collaboration_type: str,
        project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Facilitate collaboration between community members
        
        Args:
            initiator_id: User who initiated collaboration
            target_user_ids: Users to collaborate with
            collaboration_type: Type of collaboration
            project_details: Details about the collaboration project
            
        Returns:
            Collaboration facilitation result
        """
        try:
            # Verify all users are community members
            all_participants = [initiator_id] + target_user_ids
            for user_id in all_participants:
                if user_id not in self.community_members:
                    raise WorkflowError(f"User {user_id} is not a community member")
            
            # Create collaboration event
            event = await self._create_collaboration_event(
                initiator_id, target_user_ids, collaboration_type, project_details
            )
            
            # Calculate compatibility scores
            compatibility_scores = await self._calculate_collaboration_compatibility(all_participants)
            
            # Provide collaboration tips
            collaboration_tips = await self._generate_collaboration_tips(
                all_participants, collaboration_type
            )
            
            # Update contribution scores for all participants
            for user_id in all_participants:
                await self.update_contribution_score(
                    user_id, "collaboration_initiation" if user_id == initiator_id else "collaboration_participation", 
                    0.8
                )
            
            result = {
                "collaboration_id": event.event_id,
                "participants": all_participants,
                "compatibility_score": sum(compatibility_scores.values()) / len(compatibility_scores),
                "collaboration_tips": collaboration_tips,
                "estimated_success_rate": await self._estimate_collaboration_success(compatibility_scores)
            }
            
            logger.info(f"Collaboration facilitated: {event.event_id}")
            return result
            
        except Exception as e:
            logger.error(f"Collaboration facilitation failed: {e}")
            raise WorkflowError(f"Collaboration facilitation failed: {e}")
    
    async def organize_community_event(
        self,
        organizer_id: str,
        event_type: CommunityEventType,
        title: str,
        description: str,
        target_participants: List[str] = None
    ) -> CommunityEvent:
        """Organize community event"""
        
        event_id = f"event_{int(datetime.utcnow().timestamp())}"
        
        # Determine participants
        if target_participants is None:
            # Auto-select based on event type
            target_participants = await self._select_event_participants(event_type, organizer_id)
        
        event = CommunityEvent(
            event_id=event_id,
            event_type=event_type,
            title=title,
            description=description,
            participants=target_participants,
            organizer_id=organizer_id
        )
        
        # Store event
        self.community_events[event_id] = event
        
        # Notify participants
        await self._notify_event_participants(event)
        
        # Update organizer's contribution score
        await self.update_contribution_score(organizer_id, "event_organization", 1.5)
        
        logger.info(f"Community event organized: {title} ({event_id})")
        return event
    
    async def get_community_insights(self) -> Dict[str, Any]:
        """Get community health and engagement insights"""
        
        total_members = len(self.community_members)
        active_members = len([m for m in self.community_members.values() if m.is_active])
        
        # Calculate role distribution
        role_distribution = {}
        for member in self.community_members.values():
            role = member.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Calculate engagement metrics
        recent_events = [
            e for e in self.community_events.values()
            if e.created_at >= datetime.utcnow() - timedelta(days=30)
        ]
        
        # Top contributors
        top_contributors = sorted(
            self.community_members.values(),
            key=lambda x: x.contribution_score,
            reverse=True
        )[:10]
        
        insights = {
            "community_size": total_members,
            "active_members": active_members,
            "activity_rate": (active_members / total_members) * 100 if total_members > 0 else 0,
            "role_distribution": role_distribution,
            "recent_events_count": len(recent_events),
            "total_mentorship_pairs": len(self.mentorship_pairs),
            "top_contributors": [
                {
                    "user_id": m.user_id,
                    "username": m.username,
                    "contribution_score": m.contribution_score,
                    "role": m.role.value
                }
                for m in top_contributors
            ],
            "community_health_score": await self._calculate_community_health_score()
        }
        
        return insights
    
    async def _create_welcome_event(self, member -> None: CommunityMember) -> None:
        """Create welcome event for new member"""
        
        event = CommunityEvent(
            event_id=f"welcome_{member.user_id}_{int(datetime.utcnow().timestamp())}",
            event_type=CommunityEventType.WELCOME_NEW_MEMBER,
            title=f"Welcome {member.username}!",
            description=f"Please join us in welcoming {member.username} to our community!",
            participants=[member.user_id],
            organizer_id="system"
        )
        
        self.community_events[event.event_id] = event
    
    async def _suggest_connections(self, member: CommunityMember) -> List[str]:
        """Suggest potential connections for new member"""
        
        suggestions = []
        
        for other_member in self.community_members.values():
            if other_member.user_id != member.user_id and other_member.is_active:
                # Check for common interests
                common_interests = set(member.specialties) & set(other_member.specialties)
                if common_interests:
                    suggestions.append(other_member.user_id)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _find_suitable_mentor(self, mentee: CommunityMember) -> Optional[CommunityMember]:
        """Find suitable mentor for new member"""
        
        potential_mentors = [
            m for m in self.community_members.values()
            if (m.role in [CommunityRole.CONTRIBUTOR, CommunityRole.MODERATOR, 
                          CommunityRole.AMBASSADOR, CommunityRole.LEADER] and
                m.mentoring_capacity > 0 and
                m.is_active)
        ]
        
        # Find mentor with matching specialties
        for mentor in potential_mentors:
            common_specialties = set(mentor.specialties) & set(mentee.specialties)
            if common_specialties:
                return mentor
        
        # Return first available mentor if no specialty match
        return potential_mentors[0] if potential_mentors else None
    
    async def _create_mentorship_pair(self, mentor_id -> None: str, mentee_id -> None: str) -> None:
        """Create mentorship relationship"""
        
        self.mentorship_pairs[mentor_id] = mentee_id
        
        # Reduce mentor's capacity
        if mentor_id in self.community_members:
            self.community_members[mentor_id].mentoring_capacity -= 1
        
        # Create mentorship event
        event = CommunityEvent(
            event_id=f"mentorship_{mentor_id}_{mentee_id}",
            event_type=CommunityEventType.MENTORSHIP_MATCH,
            title="New Mentorship Formed",
            description="A new mentor-mentee relationship has been established",
            participants=[mentor_id, mentee_id],
            organizer_id="system"
        )
        
        self.community_events[event.event_id] = event
        
        logger.info(f"Mentorship pair created: {mentor_id} -> {mentee_id}")
    
    async def _check_role_promotion(self, member -> None: CommunityMember) -> None:
        """Check if member qualifies for role promotion"""
        
        current_role = member.role
        
        # Promotion criteria based on contribution score and reputation
        if (current_role == CommunityRole.MEMBER and 
            member.contribution_score >= 50 and 
            member.reputation_points >= 500):
            member.role = CommunityRole.CONTRIBUTOR
            member.mentoring_capacity = 2
            logger.info(f"Member {member.user_id} promoted to Contributor")
        
        elif (current_role == CommunityRole.CONTRIBUTOR and 
              member.contribution_score >= 150 and 
              member.reputation_points >= 1500):
            member.role = CommunityRole.MODERATOR
            member.mentoring_capacity = 5
            logger.info(f"Member {member.user_id} promoted to Moderator")
        
        elif (current_role == CommunityRole.MODERATOR and 
              member.contribution_score >= 300 and 
              member.reputation_points >= 3000):
            member.role = CommunityRole.AMBASSADOR
            member.mentoring_capacity = 8
            logger.info(f"Member {member.user_id} promoted to Ambassador")
    
    async def _create_collaboration_event(
        self, 
        initiator_id: str, 
        target_user_ids: List[str], 
        collaboration_type: str, 
        project_details: Dict[str, Any]
    ) -> CommunityEvent:
        """Create collaboration formation event"""
        
        event_id = f"collab_{int(datetime.utcnow().timestamp())}"
        all_participants = [initiator_id] + target_user_ids
        
        event = CommunityEvent(
            event_id=event_id,
            event_type=CommunityEventType.COLLABORATION_FORMED,
            title=f"New {collaboration_type} Collaboration",
            description=f"Collaboration formed: {project_details.get('title', 'Untitled Project')}",
            participants=all_participants,
            organizer_id=initiator_id
        )
        
        self.community_events[event_id] = event
        return event
    
    async def _calculate_collaboration_compatibility(self, participant_ids: List[str]) -> Dict[str, float]:
        """Calculate compatibility scores between collaboration participants"""
        
        compatibility_scores = {}
        
        for i, user1_id in enumerate(participant_ids):
            for user2_id in participant_ids[i+1:]:
                if user1_id in self.community_members and user2_id in self.community_members:
                    member1 = self.community_members[user1_id]
                    member2 = self.community_members[user2_id]
                    
                    # Calculate compatibility based on specialties and contribution levels
                    common_specialties = set(member1.specialties) & set(member2.specialties)
                    specialty_score = len(common_specialties) / max(len(member1.specialties), 1)
                    
                    # Contribution level compatibility
                    contribution_diff = abs(member1.contribution_score - member2.contribution_score)
                    contribution_score = max(0, 1 - (contribution_diff / 100))
                    
                    # Combined compatibility
                    compatibility = (specialty_score * 0.6 + contribution_score * 0.4)
                    compatibility_scores[f"{user1_id}_{user2_id}"] = compatibility
        
        return compatibility_scores
    
    async def _generate_collaboration_tips(self, participant_ids: List[str], collaboration_type: str) -> List[str]:
        """Generate tips for successful collaboration"""
        
        tips = [
            "Establish clear communication channels and meeting schedules",
            "Define roles and responsibilities for each team member",
            "Set measurable goals and milestones for the collaboration",
            "Share resources and knowledge openly with your collaborators",
            "Celebrate small wins and progress throughout the project"
        ]
        
        # Add type-specific tips
        if collaboration_type == "content_creation":
            tips.append("Create a shared content calendar and style guide")
        elif collaboration_type == "skill_development":
            tips.append("Schedule regular knowledge sharing sessions")
        elif collaboration_type == "business_project":
            tips.append("Define clear success metrics and KPIs")
        
        return tips[:4]  # Return top 4 tips
    
    async def _estimate_collaboration_success(self, compatibility_scores: Dict[str, float]) -> float:
        """Estimate likelihood of collaboration success"""
        
        if not compatibility_scores:
            return 0.5  # Neutral estimate
        
        avg_compatibility = sum(compatibility_scores.values()) / len(compatibility_scores)
        
        # Convert to success probability
        success_rate = 0.3 + (avg_compatibility * 0.6)  # Base 30% + up to 60% based on compatibility
        
        return round(success_rate, 3)
    
    async def _select_event_participants(self, event_type: CommunityEventType, organizer_id: str) -> List[str]:
        """Auto-select participants for community events"""
        
        participants = []
        
        if event_type == CommunityEventType.GROUP_CHALLENGE:
            # Select active members with similar contribution levels
            organizer = self.community_members.get(organizer_id)
            if organizer:
                similar_members = [
                    m.user_id for m in self.community_members.values()
                    if (m.user_id != organizer_id and m.is_active and
                        abs(m.contribution_score - organizer.contribution_score) < 20)
                ]
                participants = similar_members[:10]  # Limit to 10 participants
        
        elif event_type == CommunityEventType.KNOWLEDGE_SHARING:
            # Select members with high contribution scores
            top_contributors = sorted(
                [m for m in self.community_members.values() if m.is_active],
                key=lambda x: x.contribution_score,
                reverse=True
            )
            participants = [m.user_id for m in top_contributors[:5]]
        
        return participants
    
    async def _notify_event_participants(self, event -> None: CommunityEvent) -> None:
        """Notify participants about community event"""
        
        # In real implementation, this would send notifications
        logger.info(f"Notifying {len(event.participants)} participants about event: {event.title}")
    
    async def _calculate_community_health_score(self) -> float:
        """Calculate overall community health score"""
        
        total_members = len(self.community_members)
        if total_members == 0:
            return 0.0
        
        # Activity rate
        active_members = len([m for m in self.community_members.values() if m.is_active])
        activity_rate = active_members / total_members
        
        # Engagement rate (based on recent events)
        recent_events = len([
            e for e in self.community_events.values()
            if e.created_at >= datetime.utcnow() - timedelta(days=30)
        ])
        engagement_rate = min(recent_events / max(total_members, 1), 1.0)
        
        # Role diversity
        unique_roles = len(set(m.role for m in self.community_members.values()))
        role_diversity = unique_roles / len(CommunityRole)
        
        # Mentorship coverage
        mentorship_coverage = len(self.mentorship_pairs) / max(total_members, 1)
        
        # Combined health score
        health_score = (
            activity_rate * 0.3 +
            engagement_rate * 0.3 +
            role_diversity * 0.2 +
            mentorship_coverage * 0.2
        )
        
        return round(health_score, 3)