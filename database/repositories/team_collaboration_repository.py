"""Advanced Team Collaboration Repository

Enterprise-grade repository for creator collaboration management, intelligent
team matching, and comprehensive project coordination systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc, and_, or_, func, text
import numpy as np

from .base_repository import BaseRepository
from ..models.advanced_team_collaboration import (
    CreatorCollaboration,
    CollaborationTeamMember,
    AICollaborationMatch,
    CollaborationType,
    CollaborationStatus,
    TeamMemberRole,
    MatchingAlgorithm,
    MatchStatus
)
from ..connections.manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class AdvancedTeamCollaborationRepository(BaseRepository[CreatorCollaboration]):
    """
    Enterprise Advanced Team Collaboration Repository
    
    Manages creator collaborations, intelligent team matching, and
    comprehensive project coordination for content creators.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(CreatorCollaboration, db_session)
        self.model = CreatorCollaboration
    
    async def create_collaboration(
        self,
        initiator_user_id: str,
        collaboration_title: str,
        collaboration_type: CollaborationType,
        project_description: str,
        required_skills: List[str],
        **kwargs
    ) -> CreatorCollaboration:
        """
        Create new creator collaboration project
        
        Args:
            initiator_user_id: User UUID of collaboration initiator
            collaboration_title: Title of the collaboration
            collaboration_type: Type of collaboration
            project_description: Detailed project description
            required_skills: List of required skills
            **kwargs: Additional collaboration parameters
            
        Returns:
            Created CreatorCollaboration instance
        """
        try:
            collaboration_data = {
                "initiator_user_id": initiator_user_id,
                "collaboration_title": collaboration_title,
                "collaboration_type": collaboration_type,
                "project_description": project_description,
                "required_skills": required_skills,
                "collaboration_status": CollaborationStatus.OPEN,
                "max_team_size": kwargs.get('max_team_size', 5),
                "expected_duration_days": kwargs.get('expected_duration_days', 30),
                "budget_range_min": Decimal(str(kwargs.get('budget_range_min', 0.0))),
                "budget_range_max": Decimal(str(kwargs.get('budget_range_max', 0.0))),
                "revenue_sharing_model": kwargs.get('revenue_sharing_model', {}),
                "project_requirements": kwargs.get('project_requirements', {}),
                **kwargs
            }
            
            collaboration = CreatorCollaboration(**collaboration_data)
            
            self.db_session.add(collaboration)
            await self.db_session.commit()
            await self.db_session.refresh(collaboration)
            
            # Automatically add initiator as team leader
            await self.add_team_member(
                collaboration.id,
                initiator_user_id,
                TeamMemberRole.LEADER,
                auto_approved=True
            )
            
            logger.info(f"Created collaboration: {collaboration.id} - {collaboration_title}")
            return collaboration
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create collaboration: {str(e)}")
            raise
    
    async def add_team_member(
        self,
        collaboration_id: str,
        user_id: str,
        role: TeamMemberRole,
        skills_offered: Optional[List[str]] = None,
        auto_approved: bool = False
    ) -> CollaborationTeamMember:
        """
        Add team member to collaboration
        
        Args:
            collaboration_id: CreatorCollaboration UUID
            user_id: User UUID
            role: Team member role
            skills_offered: Skills the member brings
            auto_approved: Whether to auto-approve the member
            
        Returns:
            Created CollaborationTeamMember instance
        """
        try:
            # Check if collaboration exists and has space
            collaboration = await self.get_by_id(collaboration_id)
            if not collaboration:
                raise ValueError(f"Collaboration not found: {collaboration_id}")
            
            current_members = self.db_session.query(CollaborationTeamMember).filter(
                CollaborationTeamMember.collaboration_id == collaboration_id,
                CollaborationTeamMember.is_active == True
            ).count()
            
            if current_members >= collaboration.max_team_size:
                raise ValueError("Collaboration team is at maximum capacity")
            
            # Check if user is already a member
            existing_member = self.db_session.query(CollaborationTeamMember).filter(
                and_(
                    CollaborationTeamMember.collaboration_id == collaboration_id,
                    CollaborationTeamMember.user_id == user_id,
                    CollaborationTeamMember.is_active == True
                )
            ).first()
            
            if existing_member:
                raise ValueError("User is already a member of this collaboration")
            
            member_data = {
                "collaboration_id": collaboration_id,
                "user_id": user_id,
                "team_role": role,
                "skills_offered": skills_offered or [],
                "join_date": datetime.now(timezone.utc),
                "is_approved": auto_approved,
                "contribution_percentage": 0.0  # To be set later
            }
            
            team_member = CollaborationTeamMember(**member_data)
            
            self.db_session.add(team_member)
            
            # Update collaboration current team size
            collaboration.current_team_size = current_members + 1
            
            await self.db_session.commit()
            await self.db_session.refresh(team_member)
            
            logger.info(f"Added team member: {user_id} to collaboration: {collaboration_id}")
            return team_member
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to add team member: {str(e)}")
            raise
    
    async def approve_team_member(
        self,
        member_id: str,
        approved_by_user_id: str,
        contribution_percentage: float = 0.0
    ) -> CollaborationTeamMember:
        """
        Approve team member for collaboration
        
        Args:
            member_id: CollaborationTeamMember UUID
            approved_by_user_id: User ID of approver
            contribution_percentage: Expected contribution percentage
            
        Returns:
            Updated CollaborationTeamMember instance
        """
        try:
            team_member = self.db_session.query(CollaborationTeamMember).filter(
                CollaborationTeamMember.id == member_id
            ).first()
            
            if not team_member:
                raise ValueError(f"Team member not found: {member_id}")
            
            # Verify approver has permission (must be leader or initiator)
            collaboration = await self.get_by_id(team_member.collaboration_id)
            if not collaboration:
                raise ValueError("Associated collaboration not found")
            
            if (approved_by_user_id != collaboration.initiator_user_id and
                not self._is_team_leader(team_member.collaboration_id, approved_by_user_id)):
                raise ValueError("User does not have permission to approve team members")
            
            team_member.is_approved = True
            team_member.approved_by = approved_by_user_id
            team_member.approved_at = datetime.now(timezone.utc)
            team_member.contribution_percentage = contribution_percentage
            
            await self.db_session.commit()
            
            logger.info(f"Approved team member: {member_id} with {contribution_percentage}% contribution")
            return team_member
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to approve team member: {str(e)}")
            raise
    
    def _is_team_leader(self, collaboration_id: str, user_id: str) -> bool:
        """Check if user is a team leader in the collaboration"""
        leader = self.db_session.query(CollaborationTeamMember).filter(
            and_(
                CollaborationTeamMember.collaboration_id == collaboration_id,
                CollaborationTeamMember.user_id == user_id,
                CollaborationTeamMember.team_role == TeamMemberRole.LEADER,
                CollaborationTeamMember.is_active == True
            )
        ).first()
        return leader is not None
    
    async def create_ai_collaboration_match(
        self,
        user_id: str,
        collaboration_id: str,
        matching_algorithm: MatchingAlgorithm,
        compatibility_score: float,
        skill_alignment_score: float,
        collaboration_history_score: float,
        **kwargs
    ) -> AICollaborationMatch:
        """
        Create AI-powered collaboration match
        
        Args:
            user_id: User UUID
            collaboration_id: CreatorCollaboration UUID
            matching_algorithm: Algorithm used for matching
            compatibility_score: Overall compatibility score
            skill_alignment_score: Skills alignment score
            collaboration_history_score: Historical collaboration score
            **kwargs: Additional matching parameters
            
        Returns:
            Created AICollaborationMatch instance
        """
        try:
            # Calculate overall match score
            weights = kwargs.get('score_weights', {
                'compatibility': 0.4,
                'skill_alignment': 0.4,
                'collaboration_history': 0.2
            })
            
            overall_match_score = (
                compatibility_score * weights['compatibility'] +
                skill_alignment_score * weights['skill_alignment'] +
                collaboration_history_score * weights['collaboration_history']
            )
            
            match_data = {
                "user_id": user_id,
                "collaboration_id": collaboration_id,
                "matching_algorithm": matching_algorithm,
                "compatibility_score": compatibility_score,
                "skill_alignment_score": skill_alignment_score,
                "collaboration_history_score": collaboration_history_score,
                "overall_match_score": overall_match_score,
                "match_status": MatchStatus.SUGGESTED,
                "match_reasoning": kwargs.get('match_reasoning', {}),
                "confidence_level": kwargs.get('confidence_level', 0.0),
                **kwargs
            }
            
            ai_match = AICollaborationMatch(**match_data)
            
            self.db_session.add(ai_match)
            await self.db_session.commit()
            await self.db_session.refresh(ai_match)
            
            logger.info(f"Created AI collaboration match: {ai_match.id} with score: {overall_match_score:.2f}")
            return ai_match
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create AI collaboration match: {str(e)}")
            raise
    
    async def get_collaboration_matches(
        self,
        user_id: str,
        min_match_score: float = 0.7,
        collaboration_types: Optional[List[CollaborationType]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered collaboration matches for a user
        
        Args:
            user_id: User UUID
            min_match_score: Minimum match score threshold
            collaboration_types: Optional collaboration type filters
            limit: Maximum number of matches to return
            
        Returns:
            List of collaboration matches with details
        """
        try:
            query = self.db_session.query(
                AICollaborationMatch,
                CreatorCollaboration
            ).join(
                CreatorCollaboration,
                AICollaborationMatch.collaboration_id == CreatorCollaboration.id
            ).filter(
                and_(
                    AICollaborationMatch.user_id == user_id,
                    AICollaborationMatch.overall_match_score >= min_match_score,
                    AICollaborationMatch.match_status == MatchStatus.SUGGESTED,
                    CreatorCollaboration.collaboration_status == CollaborationStatus.OPEN
                )
            )
            
            if collaboration_types:
                query = query.filter(CreatorCollaboration.collaboration_type.in_(collaboration_types))
            
            matches = query.order_by(desc(AICollaborationMatch.overall_match_score)).limit(limit).all()
            
            # Format matches with collaboration details
            formatted_matches = []
            for ai_match, collaboration in matches:
                # Get current team information
                team_members = self.db_session.query(CollaborationTeamMember).filter(
                    and_(
                        CollaborationTeamMember.collaboration_id == collaboration.id,
                        CollaborationTeamMember.is_active == True,
                        CollaborationTeamMember.is_approved == True
                    )
                ).all()
                
                match_info = {
                    "match_id": ai_match.id,
                    "collaboration": {
                        "id": collaboration.id,
                        "title": collaboration.collaboration_title,
                        "type": collaboration.collaboration_type.value,
                        "description": collaboration.project_description,
                        "required_skills": collaboration.required_skills,
                        "current_team_size": len(team_members),
                        "max_team_size": collaboration.max_team_size,
                        "budget_range": {
                            "min": float(collaboration.budget_range_min),
                            "max": float(collaboration.budget_range_max)
                        },
                        "expected_duration_days": collaboration.expected_duration_days,
                        "created_at": collaboration.created_at.isoformat()
                    },
                    "match_scores": {
                        "overall": ai_match.overall_match_score,
                        "compatibility": ai_match.compatibility_score,
                        "skill_alignment": ai_match.skill_alignment_score,
                        "collaboration_history": ai_match.collaboration_history_score,
                        "confidence_level": ai_match.confidence_level
                    },
                    "match_reasoning": ai_match.match_reasoning,
                    "algorithm_used": ai_match.matching_algorithm.value,
                    "suggested_at": ai_match.created_at.isoformat()
                }
                
                formatted_matches.append(match_info)
            
            logger.info(f"Retrieved {len(formatted_matches)} collaboration matches for user: {user_id}")
            return formatted_matches
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get collaboration matches: {str(e)}")
            raise
    
    async def update_collaboration_status(
        self,
        collaboration_id: str,
        new_status: CollaborationStatus,
        updated_by_user_id: str,
        status_reason: Optional[str] = None
    ) -> CreatorCollaboration:
        """
        Update collaboration status
        
        Args:
            collaboration_id: CreatorCollaboration UUID
            new_status: New collaboration status
            updated_by_user_id: User ID making the update
            status_reason: Reason for status change
            
        Returns:
            Updated CreatorCollaboration instance
        """
        try:
            collaboration = await self.get_by_id(collaboration_id)
            if not collaboration:
                raise ValueError(f"Collaboration not found: {collaboration_id}")
            
            # Verify user has permission to update status
            if (updated_by_user_id != collaboration.initiator_user_id and
                not self._is_team_leader(collaboration_id, updated_by_user_id)):
                raise ValueError("User does not have permission to update collaboration status")
            
            old_status = collaboration.collaboration_status
            collaboration.collaboration_status = new_status
            
            # Set completion/cancellation dates
            if new_status == CollaborationStatus.COMPLETED:
                collaboration.actual_completion_date = datetime.now(timezone.utc)
            elif new_status == CollaborationStatus.CANCELLED:
                collaboration.cancellation_date = datetime.now(timezone.utc)
                collaboration.cancellation_reason = status_reason
            
            # Update project timeline if needed
            if hasattr(collaboration, 'project_timeline'):
                timeline = collaboration.project_timeline or {}
                timeline[f'status_change_{datetime.now().timestamp()}'] = {
                    'from_status': old_status.value,
                    'to_status': new_status.value,
                    'updated_by': updated_by_user_id,
                    'reason': status_reason,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                collaboration.project_timeline = timeline
            
            await self.db_session.commit()
            
            logger.info(f"Updated collaboration status: {collaboration_id} from {old_status.value} to {new_status.value}")
            return collaboration
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update collaboration status: {str(e)}")
            raise
    
    async def calculate_revenue_distribution(
        self,
        collaboration_id: str,
        total_revenue: Decimal
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate revenue distribution among team members
        
        Args:
            collaboration_id: CreatorCollaboration UUID
            total_revenue: Total revenue to distribute
            
        Returns:
            Dictionary containing revenue distribution details
        """
        try:
            collaboration = await self.get_by_id(collaboration_id)
            if not collaboration:
                raise ValueError(f"Collaboration not found: {collaboration_id}")
            
            # Get approved team members
            team_members = self.db_session.query(CollaborationTeamMember).filter(
                and_(
                    CollaborationTeamMember.collaboration_id == collaboration_id,
                    CollaborationTeamMember.is_active == True,
                    CollaborationTeamMember.is_approved == True
                )
            ).all()
            
            if not team_members:
                raise ValueError("No approved team members found for collaboration")
            
            # Get revenue sharing model
            sharing_model = collaboration.revenue_sharing_model or {}
            distribution_type = sharing_model.get('type', 'equal')
            
            revenue_distribution = {}
            
            if distribution_type == 'equal':
                # Equal distribution among all members
                share_per_member = total_revenue / len(team_members)
                for member in team_members:
                    revenue_distribution[member.user_id] = {
                        "amount": float(share_per_member),
                        "percentage": round(100.0 / len(team_members), 2),
                        "distribution_method": "equal",
                        "role": member.team_role.value
                    }
            
            elif distribution_type == 'contribution_based':
                # Distribution based on contribution percentages
                total_contribution = sum(member.contribution_percentage for member in team_members)
                
                if total_contribution == 0:
                    # Fallback to equal distribution
                    share_per_member = total_revenue / len(team_members)
                    for member in team_members:
                        revenue_distribution[member.user_id] = {
                            "amount": float(share_per_member),
                            "percentage": round(100.0 / len(team_members), 2),
                            "distribution_method": "equal_fallback",
                            "role": member.team_role.value
                        }
                else:
                    for member in team_members:
                        percentage = (member.contribution_percentage / total_contribution) * 100
                        amount = total_revenue * (member.contribution_percentage / total_contribution)
                        revenue_distribution[member.user_id] = {
                            "amount": float(amount),
                            "percentage": round(percentage, 2),
                            "distribution_method": "contribution_based",
                            "contribution_percentage": member.contribution_percentage,
                            "role": member.team_role.value
                        }
            
            elif distribution_type == 'role_based':
                # Distribution based on predefined role weights
                role_weights = sharing_model.get('role_weights', {
                    TeamMemberRole.LEADER.value: 0.4,
                    TeamMemberRole.CREATOR.value: 0.3,
                    TeamMemberRole.COLLABORATOR.value: 0.2,
                    TeamMemberRole.CONTRIBUTOR.value: 0.1
                })
                
                total_weight = sum(role_weights.get(member.team_role.value, 0.1) for member in team_members)
                
                for member in team_members:
                    weight = role_weights.get(member.team_role.value, 0.1)
                    percentage = (weight / total_weight) * 100
                    amount = total_revenue * (weight / total_weight)
                    revenue_distribution[member.user_id] = {
                        "amount": float(amount),
                        "percentage": round(percentage, 2),
                        "distribution_method": "role_based",
                        "role": member.team_role.value,
                        "role_weight": weight
                    }
            
            # Calculate summary
            total_distributed = sum(dist["amount"] for dist in revenue_distribution.values())
            
            distribution_summary = {
                "collaboration_id": collaboration_id,
                "total_revenue": float(total_revenue),
                "total_distributed": total_distributed,
                "distribution_type": distribution_type,
                "team_member_count": len(team_members),
                "distribution_date": datetime.now(timezone.utc).isoformat(),
                "member_distributions": revenue_distribution
            }
            
            logger.info(f"Calculated revenue distribution for collaboration: {collaboration_id}")
            return distribution_summary
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to calculate revenue distribution: {str(e)}")
            raise
    
    async def get_user_collaboration_history(
        self,
        user_id: str,
        limit: int = 50,
        include_current: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive collaboration history for a user
        
        Args:
            user_id: User UUID
            limit: Maximum number of collaborations to return
            include_current: Whether to include active collaborations
            
        Returns:
            Dictionary containing collaboration history and statistics
        """
        try:
            # Get user's team memberships
            query = self.db_session.query(
                CollaborationTeamMember,
                CreatorCollaboration
            ).join(
                CreatorCollaboration,
                CollaborationTeamMember.collaboration_id == CreatorCollaboration.id
            ).filter(
                CollaborationTeamMember.user_id == user_id
            )
            
            if not include_current:
                query = query.filter(
                    CreatorCollaboration.collaboration_status.in_([
                        CollaborationStatus.COMPLETED,
                        CollaborationStatus.CANCELLED
                    ])
                )
            
            memberships = query.order_by(desc(CreatorCollaboration.created_at)).limit(limit).all()
            
            # Process collaboration history
            collaborations = []
            role_distribution = {}
            status_distribution = {}
            type_distribution = {}
            total_revenue_earned = Decimal('0.0')
            
            for membership, collaboration in memberships:
                # Count role distribution
                role = membership.team_role.value
                role_distribution[role] = role_distribution.get(role, 0) + 1
                
                # Count status distribution
                status = collaboration.collaboration_status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
                
                # Count type distribution
                ctype = collaboration.collaboration_type.value
                type_distribution[ctype] = type_distribution.get(ctype, 0) + 1
                
                # Calculate revenue if available
                if hasattr(collaboration, 'total_revenue') and collaboration.total_revenue:
                    member_share = collaboration.total_revenue * (membership.contribution_percentage / 100)
                    total_revenue_earned += member_share
                
                collaboration_info = {
                    "collaboration_id": collaboration.id,
                    "title": collaboration.collaboration_title,
                    "type": collaboration.collaboration_type.value,
                    "status": collaboration.collaboration_status.value,
                    "user_role": membership.team_role.value,
                    "contribution_percentage": membership.contribution_percentage,
                    "join_date": membership.join_date.isoformat() if membership.join_date else None,
                    "is_approved": membership.is_approved,
                    "team_size": collaboration.current_team_size,
                    "duration_days": collaboration.expected_duration_days,
                    "created_at": collaboration.created_at.isoformat()
                }
                
                collaborations.append(collaboration_info)
            
            # Calculate success metrics
            completed_collaborations = [c for c in collaborations if c["status"] == "completed"]
            success_rate = len(completed_collaborations) / len(collaborations) * 100 if collaborations else 0
            
            # Calculate average team role
            leadership_roles = len([c for c in collaborations if c["user_role"] in ["leader", "creator"]])
            leadership_percentage = leadership_roles / len(collaborations) * 100 if collaborations else 0
            
            # Recent activity analysis
            recent_collaborations = [c for c in collaborations 
                                   if datetime.fromisoformat(c["created_at"]) >= datetime.now(timezone.utc) - timedelta(days=90)]
            
            history_summary = {
                "user_id": user_id,
                "total_collaborations": len(collaborations),
                "active_collaborations": len([c for c in collaborations if c["status"] in ["open", "in_progress"]]),
                "completed_collaborations": len(completed_collaborations),
                "cancelled_collaborations": len([c for c in collaborations if c["status"] == "cancelled"]),
                "success_rate_percentage": round(success_rate, 2),
                "leadership_percentage": round(leadership_percentage, 2),
                "total_revenue_earned": float(total_revenue_earned),
                "recent_activity_count": len(recent_collaborations),
                "distribution_analysis": {
                    "by_role": role_distribution,
                    "by_status": status_distribution,
                    "by_type": type_distribution
                },
                "collaboration_patterns": {
                    "most_common_role": max(role_distribution, key=role_distribution.get) if role_distribution else None,
                    "most_common_type": max(type_distribution, key=type_distribution.get) if type_distribution else None,
                    "average_team_size": round(np.mean([c["team_size"] for c in collaborations]), 1) if collaborations else 0,
                    "average_duration": round(np.mean([c["duration_days"] for c in collaborations]), 1) if collaborations else 0
                },
                "collaborations": collaborations
            }
            
            logger.info(f"Retrieved collaboration history for user: {user_id} - {len(collaborations)} collaborations")
            return history_summary
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user collaboration history: {str(e)}")
            raise
    
    async def get_trending_collaboration_opportunities(
        self,
        limit: int = 20,
        collaboration_types: Optional[List[CollaborationType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get trending collaboration opportunities based on activity and success metrics
        
        Args:
            limit: Maximum number of opportunities to return
            collaboration_types: Optional collaboration type filters
            
        Returns:
            List of trending collaboration opportunities
        """
        try:
            # Get recent open collaborations with activity metrics
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            query = self.db_session.query(
                CreatorCollaboration,
                func.count(CollaborationTeamMember.id).label('application_count'),
                func.count(AICollaborationMatch.id).label('ai_match_count')
            ).outerjoin(
                CollaborationTeamMember,
                and_(
                    CollaborationTeamMember.collaboration_id == CreatorCollaboration.id,
                    CollaborationTeamMember.created_at >= cutoff_date
                )
            ).outerjoin(
                AICollaborationMatch,
                and_(
                    AICollaborationMatch.collaboration_id == CreatorCollaboration.id,
                    AICollaborationMatch.created_at >= cutoff_date
                )
            ).filter(
                and_(
                    CreatorCollaboration.collaboration_status == CollaborationStatus.OPEN,
                    CreatorCollaboration.created_at >= cutoff_date
                )
            ).group_by(CreatorCollaboration.id)
            
            if collaboration_types:
                query = query.filter(CreatorCollaboration.collaboration_type.in_(collaboration_types))
            
            opportunities = query.order_by(desc('application_count'), desc('ai_match_count')).limit(limit * 2).all()
            
            # Calculate trending scores and format opportunities
            trending_opportunities = []
            
            for collaboration, application_count, ai_match_count in opportunities:
                # Calculate trending score based on various factors
                days_since_created = (datetime.now(timezone.utc) - collaboration.created_at).days
                age_factor = max(0.1, 1.0 - (days_since_created / 30.0))  # Newer collaborations get higher scores
                
                team_fill_rate = collaboration.current_team_size / collaboration.max_team_size
                urgency_factor = 1.0 + (team_fill_rate * 0.5)  # Teams closer to full get higher urgency
                
                activity_score = (application_count * 2) + ai_match_count
                trending_score = activity_score * age_factor * urgency_factor
                
                # Get budget attractiveness
                avg_budget = (collaboration.budget_range_min + collaboration.budget_range_max) / 2
                budget_score = float(avg_budget) / 1000.0  # Normalize budget score
                
                opportunity_info = {
                    "collaboration_id": collaboration.id,
                    "title": collaboration.collaboration_title,
                    "type": collaboration.collaboration_type.value,
                    "description": collaboration.project_description[:200] + "..." if len(collaboration.project_description) > 200 else collaboration.project_description,
                    "required_skills": collaboration.required_skills,
                    "team_status": {
                        "current_size": collaboration.current_team_size,
                        "max_size": collaboration.max_team_size,
                        "fill_percentage": round(team_fill_rate * 100, 1),
                        "spots_remaining": collaboration.max_team_size - collaboration.current_team_size
                    },
                    "budget_range": {
                        "min": float(collaboration.budget_range_min),
                        "max": float(collaboration.budget_range_max),
                        "average": float(avg_budget)
                    },
                    "project_timeline": {
                        "expected_duration_days": collaboration.expected_duration_days,
                        "created_at": collaboration.created_at.isoformat(),
                        "days_since_created": days_since_created
                    },
                    "activity_metrics": {
                        "recent_applications": application_count,
                        "ai_matches": ai_match_count,
                        "trending_score": round(trending_score, 2),
                        "activity_level": "high" if activity_score >= 5 else "medium" if activity_score >= 2 else "low"
                    },
                    "attractiveness_factors": {
                        "budget_attractiveness": min(5.0, budget_score),
                        "urgency_level": "high" if team_fill_rate >= 0.7 else "medium" if team_fill_rate >= 0.4 else "low",
                        "skill_demand": "high" if len(collaboration.required_skills) >= 3 else "medium"
                    }
                }
                
                trending_opportunities.append(opportunity_info)
            
            # Sort by trending score and return top opportunities
            trending_opportunities.sort(key=lambda x: x["activity_metrics"]["trending_score"], reverse=True)
            
            logger.info(f"Generated {len(trending_opportunities)} trending collaboration opportunities")
            return trending_opportunities[:limit]
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get trending collaboration opportunities: {str(e)}")
            raise
