"""
Collaboration endpoints for IA Influencer Agent platform.

This module handles collaboration features between content creators,
matching, partnerships, and joint content creation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User
from ..models.collaboration import (
    Collaboration, CollaborationCreate, CollaborationUpdate,
    CollaborationRequest, CollaborationResponse
)
from ..business.collaboration_service import CollaborationService
from ..business.matching_service import MatchingService
from ..business.notification_service import NotificationService
from ..security.auth_manager import AuthManager

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])

# Request/Response models
class CollaborationSearchRequest(BaseModel):
    """Request model for collaboration search"""
    skills_needed: List[str]
    content_types: List[str]
    experience_level: Optional[str] = None
    location_preference: Optional[str] = None
    budget_range: Optional[Dict[str, float]] = None

class PartnershipProposal(BaseModel):
    """Model for partnership proposals"""
    target_user_id: str
    project_description: str
    proposed_terms: Dict[str, Any]
    duration_days: int
    collaboration_type: str  # "content_creation", "cross_promotion", "skill_exchange"

class CollaborationInvite(BaseModel):
    """Model for collaboration invites"""
    collaboration_id: str
    invited_users: List[str]
    message: Optional[str] = None
    role_assignments: Dict[str, str]

@router.get("/discover", response_model=Dict[str, Any])
async def discover_collaborators(
    content_type: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(AuthManager.get_current_user),
    matching_service: MatchingService = Depends()
):
    """
    Discover potential collaborators based on complementary skills and needs.
    
    AI-powered matching system considers:
    - Skill complementarity
    - Content type compatibility
    - Experience levels
    - Geographic proximity (optional)
    - Past collaboration success rates
    """
    try:
        # Parse skills from query parameter
        skills_list = skills.split(",") if skills else []
        
        # Get AI-powered matches
        matches = await matching_service.find_collaboration_matches(
            user_id=current_user.id,
            content_type=content_type,
            desired_skills=skills_list,
            experience_level=experience_level,
            location=location,
            skip=skip,
            limit=limit
        )
        
        # Format match results with compatibility scores
        formatted_matches = []
        for match in matches:
            match_data = {
                "user_id": str(match["user"].id),
                "username": match["user"].username,
                "role": match["user"].role,
                "skills": match["user"].skills,
                "experience_level": match["user"].experience_level,
                "location": match["user"].location,
                "compatibility_score": match["compatibility_score"],
                "match_reasons": match["match_reasons"],
                "portfolio_highlights": match.get("portfolio_highlights", []),
                "collaboration_rating": match.get("collaboration_rating", 0),
                "response_rate": match.get("response_rate", 0),
                "profile_image": match["user"].profile_image_url
            }
            formatted_matches.append(match_data)
        
        logger.info(f"Collaboration discovery by {current_user.email}: {len(formatted_matches)} matches")
        
        return {
            "matches": formatted_matches,
            "total": len(formatted_matches),
            "search_criteria": {
                "content_type": content_type,
                "skills": skills_list,
                "experience_level": experience_level,
                "location": location
            },
            "recommendation_engine": "AI-powered compatibility matching"
        }
        
    except Exception as e:
        logger.error(f"Collaboration discovery error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to discover collaborators"
        )

@router.post("/propose", response_model=Dict[str, Any])
async def propose_partnership(
    proposal: PartnershipProposal,
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends(),
    notification_service: NotificationService = Depends()
):
    """
    Propose partnership to another user with project details and terms.
    """
    try:
        # Validate target user exists and is not the current user
        if proposal.target_user_id == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot propose partnership to yourself"
            )
        
        # Check if target user accepts collaborations
        target_user = await collaboration_service.get_user_collaboration_settings(
            proposal.target_user_id
        )
        if not target_user or not target_user.get("accepts_collaborations", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target user is not accepting collaboration proposals"
            )
        
        # Create collaboration proposal
        collaboration_data = CollaborationCreate(
            title=f"Partnership Proposal: {proposal.project_description[:50]}...",
            description=proposal.project_description,
            collaboration_type=proposal.collaboration_type,
            creator_id=current_user.id,
            status="proposed",
            proposed_terms=proposal.proposed_terms,
            duration_days=proposal.duration_days,
            invited_user_ids=[proposal.target_user_id]
        )
        
        collaboration = await collaboration_service.create_collaboration(collaboration_data)
        
        # Send notification to target user
        await notification_service.send_collaboration_proposal_notification(
            recipient_id=proposal.target_user_id,
            proposer=current_user,
            collaboration_id=str(collaboration.id),
            project_description=proposal.project_description
        )
        
        logger.info(f"Partnership proposed by {current_user.email} to {proposal.target_user_id}")
        
        return {
            "message": "Partnership proposal sent successfully",
            "collaboration_id": str(collaboration.id),
            "target_user_id": proposal.target_user_id,
            "project_type": proposal.collaboration_type,
            "status": "proposed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Propose partnership error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send partnership proposal"
        )

@router.get("/requests", response_model=Dict[str, Any])
async def get_collaboration_requests(
    status_filter: Optional[str] = Query(None, regex="^(pending|accepted|rejected|active|completed)$"),
    type_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends()
):
    """
    Get user's collaboration requests (sent and received).
    """
    try:
        # Get both sent and received collaboration requests
        sent_requests = await collaboration_service.get_user_sent_collaborations(
            user_id=current_user.id,
            status=status_filter,
            collaboration_type=type_filter,
            skip=skip,
            limit=limit
        )
        
        received_requests = await collaboration_service.get_user_received_collaborations(
            user_id=current_user.id,
            status=status_filter,
            collaboration_type=type_filter,
            skip=skip,
            limit=limit
        )
        
        # Format results
        def format_collaboration(collab, request_type):
            return {
                "collaboration_id": str(collab.id),
                "title": collab.title,
                "description": collab.description,
                "type": collab.collaboration_type,
                "status": collab.status,
                "created_at": collab.created_at,
                "updated_at": collab.updated_at,
                "duration_days": collab.duration_days,
                "request_type": request_type,
                "creator": {
                    "user_id": str(collab.creator.id),
                    "username": collab.creator.username,
                    "role": collab.creator.role
                },
                "participants": [
                    {
                        "user_id": str(p.user.id),
                        "username": p.user.username,
                        "role": p.role,
                        "status": p.status
                    }
                    for p in collab.participants
                ],
                "proposed_terms": collab.proposed_terms
            }
        
        formatted_sent = [format_collaboration(c, "sent") for c in sent_requests]
        formatted_received = [format_collaboration(c, "received") for c in received_requests]
        
        return {
            "sent_requests": formatted_sent,
            "received_requests": formatted_received,
            "total_sent": len(formatted_sent),
            "total_received": len(formatted_received),
            "filters": {
                "status": status_filter,
                "type": type_filter
            }
        }
        
    except Exception as e:
        logger.error(f"Get collaboration requests error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collaboration requests"
        )

@router.post("/{collaboration_id}/respond", response_model=Dict[str, Any])
async def respond_to_collaboration(
    collaboration_id: str,
    response_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends(),
    notification_service: NotificationService = Depends()
):
    """
    Respond to collaboration request (accept/reject/negotiate).
    """
    try:
        action = response_data.get("action")  # "accept", "reject", "negotiate"
        message = response_data.get("message", "")
        counter_terms = response_data.get("counter_terms")
        
        if action not in ["accept", "reject", "negotiate"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Must be 'accept', 'reject', or 'negotiate'"
            )
        
        # Get collaboration and verify user is invited
        collaboration = await collaboration_service.get_collaboration_by_id(collaboration_id)
        if not collaboration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collaboration not found"
            )
        
        # Check if user is invited to this collaboration
        if not await collaboration_service.is_user_invited(collaboration_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not invited to this collaboration"
            )
        
        # Process response
        if action == "accept":
            updated_collaboration = await collaboration_service.accept_collaboration(
                collaboration_id, current_user.id, message
            )
            status_msg = "Collaboration accepted successfully"
            
        elif action == "reject":
            updated_collaboration = await collaboration_service.reject_collaboration(
                collaboration_id, current_user.id, message
            )
            status_msg = "Collaboration rejected"
            
        else:  # negotiate
            if not counter_terms:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Counter terms required for negotiation"
                )
            updated_collaboration = await collaboration_service.negotiate_collaboration(
                collaboration_id, current_user.id, counter_terms, message
            )
            status_msg = "Counter-proposal sent"
        
        # Send notification to collaboration creator
        await notification_service.send_collaboration_response_notification(
            recipient_id=str(collaboration.creator_id),
            responder=current_user,
            collaboration_id=collaboration_id,
            action=action,
            message=message
        )
        
        logger.info(f"Collaboration response by {current_user.email}: {action} for {collaboration_id}")
        
        return {
            "message": status_msg,
            "collaboration_id": collaboration_id,
            "action": action,
            "new_status": updated_collaboration.status,
            "response_message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Collaboration response error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process collaboration response"
        )

@router.get("/{collaboration_id}", response_model=Dict[str, Any])
async def get_collaboration_details(
    collaboration_id: str,
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends()
):
    """
    Get detailed information about a specific collaboration.
    """
    try:
        collaboration = await collaboration_service.get_collaboration_with_details(collaboration_id)
        if not collaboration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collaboration not found"
            )
        
        # Check if user has access to this collaboration
        if not await collaboration_service.user_has_access(collaboration_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get collaboration activities/timeline
        activities = await collaboration_service.get_collaboration_activities(collaboration_id)
        
        # Get shared content/deliverables
        shared_content = await collaboration_service.get_collaboration_content(collaboration_id)
        
        return {
            "collaboration_id": str(collaboration.id),
            "title": collaboration.title,
            "description": collaboration.description,
            "type": collaboration.collaboration_type,
            "status": collaboration.status,
            "created_at": collaboration.created_at,
            "updated_at": collaboration.updated_at,
            "duration_days": collaboration.duration_days,
            "proposed_terms": collaboration.proposed_terms,
            "agreed_terms": collaboration.agreed_terms,
            "creator": {
                "user_id": str(collaboration.creator.id),
                "username": collaboration.creator.username,
                "role": collaboration.creator.role,
                "profile_image": collaboration.creator.profile_image_url
            },
            "participants": [
                {
                    "user_id": str(p.user.id),
                    "username": p.user.username,
                    "role": p.role,
                    "status": p.status,
                    "joined_at": p.joined_at,
                    "contribution_score": p.contribution_score
                }
                for p in collaboration.participants
            ],
            "activities": activities,
            "shared_content": shared_content,
            "progress_percentage": collaboration.progress_percentage,
            "deadline": collaboration.deadline
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get collaboration details error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collaboration details"
        )

@router.post("/{collaboration_id}/invite", response_model=Dict[str, Any])
async def invite_users_to_collaboration(
    collaboration_id: str,
    invite_data: CollaborationInvite,
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends(),
    notification_service: NotificationService = Depends()
):
    """
    Invite additional users to an active collaboration.
    """
    try:
        # Verify user is collaboration creator or has admin role
        collaboration = await collaboration_service.get_collaboration_by_id(collaboration_id)
        if not collaboration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collaboration not found"
            )
        
        if collaboration.creator_id != current_user.id:
            # Check if user has admin role in collaboration
            user_role = await collaboration_service.get_user_role_in_collaboration(
                collaboration_id, current_user.id
            )
            if user_role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only collaboration creator or admin can invite users"
                )
        
        # Process invitations
        invitation_results = []
        for user_id in invite_data.invited_users:
            try:
                # Check if user is already in collaboration
                if await collaboration_service.is_user_in_collaboration(collaboration_id, user_id):
                    invitation_results.append({
                        "user_id": user_id,
                        "status": "already_member",
                        "message": "User is already in this collaboration"
                    })
                    continue
                
                # Send invitation
                role = invite_data.role_assignments.get(user_id, "collaborator")
                invitation = await collaboration_service.invite_user_to_collaboration(
                    collaboration_id, user_id, role, invite_data.message
                )
                
                # Send notification
                await notification_service.send_collaboration_invitation_notification(
                    recipient_id=user_id,
                    inviter=current_user,
                    collaboration_id=collaboration_id,
                    role=role,
                    message=invite_data.message
                )
                
                invitation_results.append({
                    "user_id": user_id,
                    "status": "invited",
                    "role": role,
                    "invitation_id": str(invitation.id)
                })
                
            except Exception as e:
                invitation_results.append({
                    "user_id": user_id,
                    "status": "failed",
                    "message": str(e)
                })
        
        logger.info(f"Collaboration invites sent by {current_user.email} for {collaboration_id}")
        
        return {
            "message": "Collaboration invitations processed",
            "collaboration_id": collaboration_id,
            "invitations": invitation_results,
            "total_sent": len([r for r in invitation_results if r["status"] == "invited"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invite users to collaboration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send collaboration invitations"
        )

@router.put("/{collaboration_id}/update", response_model=Dict[str, Any])
async def update_collaboration(
    collaboration_id: str,
    collaboration_update: CollaborationUpdate,
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends()
):
    """
    Update collaboration details and progress.
    """
    try:
        # Verify user has permission to update
        collaboration = await collaboration_service.get_collaboration_by_id(collaboration_id)
        if not collaboration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collaboration not found"
            )
        
        if not await collaboration_service.user_can_edit(collaboration_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied to update collaboration"
            )
        
        # Update collaboration
        updated_collaboration = await collaboration_service.update_collaboration(
            collaboration_id, collaboration_update
        )
        
        # Log activity
        await collaboration_service.log_collaboration_activity(
            collaboration_id,
            current_user.id,
            "collaboration_updated",
            f"Collaboration updated by {current_user.username}"
        )
        
        logger.info(f"Collaboration updated: {collaboration_id} by {current_user.email}")
        
        return {
            "message": "Collaboration updated successfully",
            "collaboration_id": str(updated_collaboration.id),
            "updated_fields": collaboration_update.dict(exclude_unset=True),
            "new_status": updated_collaboration.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update collaboration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update collaboration"
        )

@router.post("/{collaboration_id}/complete", response_model=Dict[str, Any])
async def complete_collaboration(
    collaboration_id: str,
    completion_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(AuthManager.get_current_user),
    collaboration_service: CollaborationService = Depends(),
    notification_service: NotificationService = Depends()
):
    """
    Mark collaboration as completed and handle final deliverables.
    """
    try:
        # Verify user has permission to complete
        if not await collaboration_service.user_can_complete(collaboration_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied to complete collaboration"
            )
        
        # Process completion
        completion_result = await collaboration_service.complete_collaboration(
            collaboration_id,
            current_user.id,
            completion_data.get("final_deliverables", []),
            completion_data.get("success_metrics", {}),
            completion_data.get("feedback", "")
        )
        
        # Send completion notifications to all participants
        participants = await collaboration_service.get_collaboration_participants(collaboration_id)
        for participant in participants:
            if participant.user.id != current_user.id:
                await notification_service.send_collaboration_completion_notification(
                    recipient_id=str(participant.user.id),
                    completer=current_user,
                    collaboration_id=collaboration_id,
                    success_metrics=completion_data.get("success_metrics", {})
                )
        
        logger.info(f"Collaboration completed: {collaboration_id} by {current_user.email}")
        
        return {
            "message": "Collaboration completed successfully",
            "collaboration_id": collaboration_id,
            "completion_date": completion_result["completion_date"],
            "final_deliverables": completion_result["final_deliverables"],
            "success_metrics": completion_result["success_metrics"],
            "participant_ratings": completion_result.get("participant_ratings", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete collaboration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete collaboration"
        )
