"""
Collaboration service for IA Influencer Agent platform.

This service handles all collaboration features including project creation,
user matching, partnership management, and collaborative content creation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.collaboration import (
    Collaboration, CollaborationCreate, CollaborationUpdate,
    CollaborationParticipant, CollaborationInvitation
)
from ..models.user import User
from ..business.matching_service import MatchingService
from ..business.notification_service import NotificationService

logger = logging.getLogger(__name__)
settings = get_settings()

class CollaborationService:
    """
    Comprehensive collaboration management service.
    
    Features:
    - Project-based collaboration creation
    - Skill-based user matching
    - Role assignment and management
    - Progress tracking and deliverables
    - Revenue sharing and contracts
    - Quality assurance and reviews
    """
    
    def __init__(self):
        self.matching_service = MatchingService()
        self.notification_service = NotificationService()
    
    async def create_collaboration(self, collaboration_data: CollaborationCreate, db: Session = None) -> Collaboration:
        """
        Create new collaboration project with initial setup.
        
        Args:
            collaboration_data: Collaboration creation data
            db: Database session
            
        Returns:
            Created collaboration instance
        """



        try:
            if not db:
                db = next(get_db())
            
            # Validate collaboration data
            if not collaboration_data.title or not collaboration_data.creator_id:
                raise ValueError("Title and creator ID are required")
            
            # Create collaboration instance
            collaboration = Collaboration(
                id=uuid.uuid4(),
                title=collaboration_data.title,
                description=collaboration_data.description,
                collaboration_type=collaboration_data.collaboration_type,
                creator_id=collaboration_data.creator_id,
                status="proposed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                duration_days=collaboration_data.duration_days,
                proposed_terms=collaboration_data.proposed_terms,
                max_participants=getattr(collaboration_data, 'max_participants', 10),
                is_active=True,
                progress_percentage=0
            )
            
            # Set deadline if duration is specified
            if collaboration_data.duration_days:
                collaboration.deadline = datetime.utcnow() + timedelta(days=collaboration_data.duration_days)
            
            # Save collaboration
            db.add(collaboration)
            db.commit()
            db.refresh(collaboration)
            
            # Add creator as first participant (admin role)
            creator_participant = CollaborationParticipant(
                collaboration_id=collaboration.id,
                user_id=collaboration_data.creator_id,
                role="admin",
                status="active",
                joined_at=datetime.utcnow(),
                contribution_score=0
            )
            
            db.add(creator_participant)
            
            # Send invitations if users specified
            if hasattr(collaboration_data, 'invited_user_ids') and collaboration_data.invited_user_ids:
                for user_id in collaboration_data.invited_user_ids:
                    await self._create_collaboration_invitation(
                        str(collaboration.id), user_id, "collaborator", db
                    )
            
            db.commit()
            
            # Log collaboration creation activity
            await self.log_collaboration_activity(
                str(collaboration.id),
                collaboration_data.creator_id,
                "collaboration_created",
                f"Collaboration '{collaboration.title}' created"
            )
            
            logger.info(f"Collaboration created: {collaboration.id}")
            return collaboration
            
        except Exception as e:
            logger.error(f"Collaboration creation error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def get_collaboration_by_id(self, collaboration_id: str, db: Session = None) -> Optional[Collaboration]:
        """Get collaboration by ID with related data"""



        try:
            if not db:
                db = next(get_db())
            
            return db.query(Collaboration).filter(
                and_(Collaboration.id == collaboration_id, Collaboration.is_active == True)
            ).first()
            
        except Exception as e:
            logger.error(f"Get collaboration error: {str(e)}")
            return None
    
    async def get_collaboration_with_details(self, collaboration_id: str, db: Session = None) -> Optional[Collaboration]:
        """Get collaboration with full details including participants and activities"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(
                and_(Collaboration.id == collaboration_id, Collaboration.is_active == True)
            ).first()
            
            if not collaboration:
                return None
            
            # Load related data
            participants = db.query(CollaborationParticipant).filter(
                CollaborationParticipant.collaboration_id == collaboration_id
            ).all()
            
            collaboration.participants = participants
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Get collaboration details error: {str(e)}")
            return None
    
    async def get_user_sent_collaborations(
        self,
        user_id: str,
        status: Optional[str] = None,
        collaboration_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        db: Session = None
    ) -> List[Collaboration]:
        """Get collaborations created by user"""



        try:
            if not db:
                db = next(get_db())
            
            query = db.query(Collaboration).filter(
                and_(Collaboration.creator_id == user_id, Collaboration.is_active == True)
            )
            
            if status:
                query = query.filter(Collaboration.status == status)
            if collaboration_type:
                query = query.filter(Collaboration.collaboration_type == collaboration_type)
            
            return query.order_by(desc(Collaboration.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Get user sent collaborations error: {str(e)}")
            return []
    
    async def get_user_received_collaborations(
        self,
        user_id: str,
        status: Optional[str] = None,
        collaboration_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        db: Session = None
    ) -> List[Collaboration]:
        """Get collaborations where user is invited/participating"""



        try:
            if not db:
                db = next(get_db())
            
            # Get collaborations where user is a participant or has invitation
            participant_collabs = db.query(Collaboration).join(CollaborationParticipant).filter(
                and_(
                    CollaborationParticipant.user_id == user_id,
                    Collaboration.is_active == True,
                    Collaboration.creator_id != user_id  # Exclude own collaborations
                )
            )
            
            if status:
                participant_collabs = participant_collabs.filter(Collaboration.status == status)
            if collaboration_type:
                participant_collabs = participant_collabs.filter(Collaboration.collaboration_type == collaboration_type)
            
            return participant_collabs.order_by(desc(Collaboration.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Get user received collaborations error: {str(e)}")
            return []
    
    async def is_user_invited(self, collaboration_id: str, user_id: str, db: Session = None) -> bool:
        """Check if user is invited to collaboration"""



        try:
            if not db:
                db = next(get_db())
            
            invitation = db.query(CollaborationInvitation).filter(
                and_(
                    CollaborationInvitation.collaboration_id == collaboration_id,
                    CollaborationInvitation.invited_user_id == user_id,
                    CollaborationInvitation.status == "pending"
                )
            ).first()
            
            return invitation is not None
            
        except Exception as e:
            logger.error(f"Check user invitation error: {str(e)}")
            return False
    
    async def accept_collaboration(self, collaboration_id: str, user_id: str, message: str = "", db: Session = None) -> Collaboration:
        """Accept collaboration invitation"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                raise ValueError("Collaboration not found")
            
            # Update invitation status
            invitation = db.query(CollaborationInvitation).filter(
                and_(
                    CollaborationInvitation.collaboration_id == collaboration_id,
                    CollaborationInvitation.invited_user_id == user_id,
                    CollaborationInvitation.status == "pending"
                )
            ).first()
            
            if invitation:
                invitation.status = "accepted"
                invitation.response_message = message
                invitation.responded_at = datetime.utcnow()
            
            # Add user as participant
            participant = CollaborationParticipant(
                collaboration_id=collaboration_id,
                user_id=user_id,
                role=invitation.role if invitation else "collaborator",
                status="active",
                joined_at=datetime.utcnow(),
                contribution_score=0
            )
            
            db.add(participant)
            
            # Update collaboration status if needed
            if collaboration.status == "proposed":
                collaboration.status = "active"
            
            collaboration.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(collaboration)
            
            # Log activity
            await self.log_collaboration_activity(
                collaboration_id,
                user_id,
                "collaboration_accepted",
                f"User accepted collaboration invitation: {message}"
            )
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Accept collaboration error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def reject_collaboration(self, collaboration_id: str, user_id: str, message: str = "", db: Session = None) -> Collaboration:
        """Reject collaboration invitation"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                raise ValueError("Collaboration not found")
            
            # Update invitation status
            invitation = db.query(CollaborationInvitation).filter(
                and_(
                    CollaborationInvitation.collaboration_id == collaboration_id,
                    CollaborationInvitation.invited_user_id == user_id,
                    CollaborationInvitation.status == "pending"
                )
            ).first()
            
            if invitation:
                invitation.status = "rejected"
                invitation.response_message = message
                invitation.responded_at = datetime.utcnow()
            
            collaboration.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(collaboration)
            
            # Log activity
            await self.log_collaboration_activity(
                collaboration_id,
                user_id,
                "collaboration_rejected",
                f"User rejected collaboration invitation: {message}"
            )
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Reject collaboration error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def negotiate_collaboration(
        self, 
        collaboration_id: str, 
        user_id: str, 
        counter_terms: Dict[str, Any], 
        message: str = "",
        db: Session = None
    ) -> Collaboration:
        """Negotiate collaboration terms"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                raise ValueError("Collaboration not found")
            
            # Update invitation with counter-terms
            invitation = db.query(CollaborationInvitation).filter(
                and_(
                    CollaborationInvitation.collaboration_id == collaboration_id,
                    CollaborationInvitation.invited_user_id == user_id,
                    CollaborationInvitation.status == "pending"
                )
            ).first()
            
            if invitation:
                invitation.status = "negotiating"
                invitation.counter_terms = counter_terms
                invitation.response_message = message
                invitation.responded_at = datetime.utcnow()
            
            # Update collaboration status
            collaboration.status = "negotiating"
            collaboration.counter_terms = counter_terms
            collaboration.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(collaboration)
            
            # Log activity
            await self.log_collaboration_activity(
                collaboration_id,
                user_id,
                "collaboration_negotiated",
                f"User proposed counter-terms: {message}"
            )
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Negotiate collaboration error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def update_collaboration(
        self, 
        collaboration_id: str, 
        collaboration_update: CollaborationUpdate, 
        db: Session = None
    ) -> Optional[Collaboration]:
        """Update collaboration details"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                return None
            
            # Apply updates
            update_data = collaboration_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(collaboration, field):
                    setattr(collaboration, field, value)
            
            collaboration.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(collaboration)
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Update collaboration error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def user_has_access(self, collaboration_id: str, user_id: str, db: Session = None) -> bool:
        """Check if user has access to collaboration"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                return False
            
            # Creator has access
            if str(collaboration.creator_id) == str(user_id):
                return True
            
            # Check if user is participant
            participant = db.query(CollaborationParticipant).filter(
                and_(
                    CollaborationParticipant.collaboration_id == collaboration_id,
                    CollaborationParticipant.user_id == user_id
                )
            ).first()
            
            return participant is not None
            
        except Exception as e:
            logger.error(f"Check collaboration access error: {str(e)}")
            return False
    
    async def user_can_edit(self, collaboration_id: str, user_id: str, db: Session = None) -> bool:
        """Check if user can edit collaboration"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                return False
            
            # Creator can edit
            if str(collaboration.creator_id) == str(user_id):
                return True
            
            # Check if user has admin role
            participant = db.query(CollaborationParticipant).filter(
                and_(
                    CollaborationParticipant.collaboration_id == collaboration_id,
                    CollaborationParticipant.user_id == user_id,
                    CollaborationParticipant.role == "admin"
                )
            ).first()
            
            return participant is not None
            
        except Exception as e:
            logger.error(f"Check edit permission error: {str(e)}")
            return False
    
    async def user_can_complete(self, collaboration_id: str, user_id: str, db: Session = None) -> bool:
        """Check if user can mark collaboration as completed"""



        return await self.user_can_edit(collaboration_id, user_id, db)
    
    async def complete_collaboration(
        self,
        collaboration_id: str,
        user_id: str,
        final_deliverables: List[Dict[str, Any]],
        success_metrics: Dict[str, Any],
        feedback: str = "",
        db: Session = None
    ) -> Dict[str, Any]:
        """Mark collaboration as completed"""



        try:
            if not db:
                db = next(get_db())
            
            collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
            if not collaboration:
                raise ValueError("Collaboration not found")
            
            # Update collaboration status
            collaboration.status = "completed"
            collaboration.completed_at = datetime.utcnow()
            collaboration.completed_by = user_id
            collaboration.final_deliverables = final_deliverables
            collaboration.success_metrics = success_metrics
            collaboration.completion_feedback = feedback
            collaboration.progress_percentage = 100
            
            db.commit()
            
            # Calculate participant ratings and contributions
            participant_ratings = await self._calculate_participant_ratings(collaboration_id, db)
            
            # Log completion activity
            await self.log_collaboration_activity(
                collaboration_id,
                user_id,
                "collaboration_completed",
                f"Collaboration completed with {len(final_deliverables)} deliverables"
            )
            
            return {
                "completion_date": collaboration.completed_at.isoformat(),
                "final_deliverables": final_deliverables,
                "success_metrics": success_metrics,
                "participant_ratings": participant_ratings
            }
            
        except Exception as e:
            logger.error(f"Complete collaboration error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def get_collaboration_activities(self, collaboration_id: str, db: Session = None) -> List[Dict[str, Any]]:
        """Get collaboration activity timeline"""



        try:
            # This would integrate with an activity/timeline table
            # Simplified implementation for now
            activities = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user": "system",
                    "action": "collaboration_created",
                    "description": "Collaboration was created"
                }
            ]
            
            return activities
            
        except Exception as e:
            logger.error(f"Get collaboration activities error: {str(e)}")
            return []
    
    async def get_collaboration_content(self, collaboration_id: str, db: Session = None) -> List[Dict[str, Any]]:
        """Get content shared within collaboration"""



        try:
            # This would integrate with content sharing functionality
            # Simplified implementation for now
            shared_content = []
            
            return shared_content
            
        except Exception as e:
            logger.error(f"Get collaboration content error: {str(e)}")
            return []
    
    async def log_collaboration_activity(
        self, 
        collaboration_id: str, 
        user_id: str, 
        activity_type: str, 
        description: str,
        db: Session = None
    ) -> None:
        """Log collaboration activity"""



        try:
            # This would log to an activity table
            # Simplified for now
            logger.info(f"Collaboration activity: {collaboration_id} - {activity_type} - {description}")
            
        except Exception as e:
            logger.error(f"Log collaboration activity error: {str(e)}")
    
    async def get_user_collaboration_settings(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Get user's collaboration preferences and settings"""



        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Return user collaboration settings
            return {
                "accepts_collaborations": getattr(user, 'accepts_collaborations', True),
                "collaboration_preferences": getattr(user, 'collaboration_preferences', {}),
                "availability": getattr(user, 'availability', 'available')
            }
            
        except Exception as e:
            logger.error(f"Get user collaboration settings error: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _create_collaboration_invitation(
        self, 
        collaboration_id: str, 
        user_id: str, 
        role: str = "collaborator",
        db: Session = None
    ) -> CollaborationInvitation:
        """Create collaboration invitation"""



        try:
            if not db:
                db = next(get_db())
            
            invitation = CollaborationInvitation(
                id=str(uuid.uuid4()),
                collaboration_id=collaboration_id,
                invited_user_id=user_id,
                role=role,
                status="pending",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days to respond
            )
            
            db.add(invitation)
            db.commit()
            
            return invitation
            
        except Exception as e:
            logger.error(f"Create collaboration invitation error: {str(e)}")
            raise
    
    async def _calculate_participant_ratings(self, collaboration_id: str, db: Session = None) -> Dict[str, Any]:
        """Calculate participant ratings and contributions"""



        try:
            # This would implement a rating system based on:
            # - Contribution quality
            # - Timeliness
            # - Communication
            # - Deliverable completion
            
            # Simplified implementation
            return {"ratings_calculated": True}
            
        except Exception as e:
            logger.error(f"Calculate participant ratings error: {str(e)}")
            return {}
