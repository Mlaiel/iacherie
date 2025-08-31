"""Collaboration API Routes
Creator matching and partnership management endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import asyncio

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...ai_agents.collaboration.matching_engine import CollaborationMatchingEngine
from ...ai_agents.collaboration.compatibility_analyzer import CompatibilityAnalyzer
from ...services.collaboration_engine import CollaborationEngine


# Enums
class CollaborationType(str, Enum):
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_VENTURES = "joint_ventures"
    LICENSING_PARTNERSHIP = "licensing_partnership"
    MENTORSHIP = "mentorship"
    REMIX_COLLABORATION = "remix_collaboration"


class CollaborationStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


# Pydantic models
class CreatorProfile(BaseModel):
    creator_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage_name: str = Field(..., min_length=1, max_length=100)
    genres: List[str] = Field(..., min_items=1, max_items=10)
    skills: List[str] = Field(..., min_items=1, max_items=20)
    skill_levels: Dict[str, SkillLevel]
    bio: str = Field(..., max_length=1000)
    location: Optional[str] = None
    languages: List[str] = Field(default=["english"])
    social_media: Dict[str, str] = Field(default={})
    portfolio_links: List[str] = Field(default=[])
    collaboration_preferences: Dict[str, Any] = Field(default={})
    availability: Dict[str, bool] = Field(default={})
    price_range: Optional[Dict[str, float]] = None


class CollaborationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=2000)
    collaboration_type: CollaborationType
    genres: List[str] = Field(..., min_items=1)
    required_skills: List[str] = Field(..., min_items=1)
    budget_range: Optional[Dict[str, float]] = None
    timeline: Dict[str, str]  # start_date, end_date, milestones
    location_requirement: Optional[str] = None
    remote_friendly: bool = Field(default=True)
    experience_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    collaboration_split: Optional[Dict[str, float]] = None
    additional_requirements: Optional[str] = None


class CollaborationMatch(BaseModel):
    match_id: str
    requester_id: str
    matched_creator_id: str
    collaboration_request_id: str
    compatibility_score: float
    match_reasons: List[str]
    shared_genres: List[str]
    complementary_skills: List[str]
    estimated_success_rate: float
    ai_recommendation: str
    match_created_at: datetime


class CollaborationProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_request_id: str
    proposer_id: str
    proposal_message: str = Field(..., max_length=1000)
    proposed_terms: Dict[str, Any]
    portfolio_samples: List[str] = Field(default=[])
    availability_details: str = Field(..., max_length=500)
    proposed_timeline: Dict[str, str]
    budget_proposal: Optional[float] = None


class CollaborationProject(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    participants: List[str]  # user_ids
    collaboration_type: CollaborationType
    status: CollaborationStatus
    project_details: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    shared_resources: List[str]
    communication_channels: Dict[str, str]
    revenue_split: Dict[str, float]
    contract_terms: Optional[str] = None


class CollaborationReview(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    reviewer_id: str
    reviewed_user_id: str
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(..., max_length=1000)
    collaboration_aspects: Dict[str, int]  # communication, creativity, professionalism, etc.
    would_collaborate_again: bool


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize collaboration components
matching_engine = CollaborationMatchingEngine()
compatibility_analyzer = CompatibilityAnalyzer()
collaboration_engine = CollaborationEngine()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/profile", response_model=Dict[str, str])
async def create_creator_profile(
    profile: CreatorProfile,
    user: dict = Depends(get_current_user)
):
    """Create or update creator profile for collaboration matching"""    try:
        # Validate skill levels match skills
        for skill in profile.skills:
            if skill not in profile.skill_levels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Skill level required for skill: {skill}"
                )
        
        # Create or update profile
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO creator_profiles (creator_id, user_id, stage_name, genres, skills,
                                            skill_levels, bio, location, languages, social_media,
                                            portfolio_links, collaboration_preferences, availability,
                                            price_range, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    stage_name = EXCLUDED.stage_name,
                    genres = EXCLUDED.genres,
                    skills = EXCLUDED.skills,
                    skill_levels = EXCLUDED.skill_levels,
                    bio = EXCLUDED.bio,
                    location = EXCLUDED.location,
                    languages = EXCLUDED.languages,
                    social_media = EXCLUDED.social_media,
                    portfolio_links = EXCLUDED.portfolio_links,
                    collaboration_preferences = EXCLUDED.collaboration_preferences,
                    availability = EXCLUDED.availability,
                    price_range = EXCLUDED.price_range,
                    updated_at = EXCLUDED.updated_at
            """, (
                profile.creator_id, user['user_id'], profile.stage_name, profile.genres,
                profile.skills, {k: v.value for k, v in profile.skill_levels.items()}, profile.bio,
                profile.location, profile.languages, profile.social_media, profile.portfolio_links,
                profile.collaboration_preferences, profile.availability, profile.price_range,
                datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Update AI matching vectors
        await matching_engine.update_creator_vectors(profile.creator_id, profile)
        
        logger.info(f"Creator profile created/updated: {profile.creator_id} for user {user['user_id']}")
        
        return {
            "creator_id": profile.creator_id,
            "message": "Creator profile created/updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Create creator profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create creator profile"
        )


@router.post("/requests", response_model=Dict[str, str])
async def create_collaboration_request(
    request: CollaborationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create a new collaboration request"""    try:
        # Verify user has creator profile
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT creator_id FROM creator_profiles WHERE user_id = %s
            """, (user['user_id'],))
            
            creator_profile = result.fetchone()
            if not creator_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creator profile required to create collaboration requests"
                )
        
        creator_id = creator_profile[0]
        
        # Create collaboration request
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO collaboration_requests (request_id, creator_id, user_id, title,
                                                  description, collaboration_type, genres,
                                                  required_skills, budget_range, timeline,
                                                  location_requirement, remote_friendly,
                                                  experience_level, collaboration_split,
                                                  additional_requirements, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.request_id, creator_id, user['user_id'], request.title,
                request.description, request.collaboration_type.value, request.genres,
                request.required_skills, request.budget_range, request.timeline,
                request.location_requirement, request.remote_friendly,
                request.experience_level.value, request.collaboration_split,
                request.additional_requirements, "open", datetime.utcnow()
            ))
            await session.commit()
        
        # Start AI matching process
        background_tasks.add_task(
            _find_collaboration_matches, request.request_id, creator_id
        )
        
        logger.info(f"Collaboration request created: {request.request_id} by user {user['user_id']}")
        
        return {
            "request_id": request.request_id,
            "message": "Collaboration request created successfully",
            "status": "open"
        }
        
    except Exception as e:
        logger.error(f"Create collaboration request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create collaboration request"
        )


@router.get("/matches", response_model=List[CollaborationMatch])
async def get_collaboration_matches(
    request_id: Optional[str] = None,
    min_score: float = Field(default=0.7, ge=0.0, le=1.0),
    user: dict = Depends(get_current_user)
):
    """Get AI-generated collaboration matches"""    try:
        query = """            SELECT cm.match_id, cm.requester_id, cm.matched_creator_id, cm.collaboration_request_id,
                   cm.compatibility_score, cm.match_reasons, cm.shared_genres,
                   cm.complementary_skills, cm.estimated_success_rate, cm.ai_recommendation,
                   cm.created_at
            FROM collaboration_matches cm
            JOIN collaboration_requests cr ON cm.collaboration_request_id = cr.request_id
            WHERE cr.user_id = %s AND cm.compatibility_score >= %s
        """        params = [user['user_id'], min_score]
        
        if request_id:
            query += " AND cm.collaboration_request_id = %s"
            params.append(request_id)
            
        query += " ORDER BY cm.compatibility_score DESC, cm.created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            matches = result.fetchall()
        
        match_list = []
        for match in matches:
            match_list.append(CollaborationMatch(
                match_id=match[0],
                requester_id=match[1],
                matched_creator_id=match[2],
                collaboration_request_id=match[3],
                compatibility_score=match[4],
                match_reasons=match[5],
                shared_genres=match[6],
                complementary_skills=match[7],
                estimated_success_rate=match[8],
                ai_recommendation=match[9],
                match_created_at=match[10]
            ))
        
        return match_list
        
    except Exception as e:
        logger.error(f"Get collaboration matches failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collaboration matches"
        )


@router.post("/proposals", response_model=Dict[str, str])
async def submit_collaboration_proposal(
    proposal: CollaborationProposal,
    user: dict = Depends(get_current_user)
):
    """Submit a proposal for a collaboration request"""    try:
        # Verify collaboration request exists and is open
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT cr.request_id, cr.user_id, cr.status
                FROM collaboration_requests cr
                WHERE cr.request_id = %s
            """, (proposal.collaboration_request_id,))
            
            request_info = result.fetchone()
            if not request_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Collaboration request not found"
                )
            
            if request_info[2] != "open":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Collaboration request is not open for proposals"
                )
            
            # Cannot propose to own request
            if request_info[1] == user['user_id']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot propose to your own collaboration request"
                )
            
            # Get proposer's creator profile
            result = await session.execute("""                SELECT creator_id FROM creator_profiles WHERE user_id = %s
            """, (user['user_id'],))
            
            creator_profile = result.fetchone()
            if not creator_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creator profile required to submit proposals"
                )
        
        proposer_creator_id = creator_profile[0]
        
        # Create proposal
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO collaboration_proposals (proposal_id, collaboration_request_id,
                                                   proposer_id, proposer_creator_id, proposal_message,
                                                   proposed_terms, portfolio_samples, availability_details,
                                                   proposed_timeline, budget_proposal, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                proposal.proposal_id, proposal.collaboration_request_id, user['user_id'],
                proposer_creator_id, proposal.proposal_message, proposal.proposed_terms,
                proposal.portfolio_samples, proposal.availability_details,
                proposal.proposed_timeline, proposal.budget_proposal, "pending", datetime.utcnow()
            ))
            await session.commit()
        
        # Generate AI compatibility analysis
        compatibility_analysis = await compatibility_analyzer.analyze_proposal_compatibility(
            proposal.collaboration_request_id, proposer_creator_id
        )
        
        # Update proposal with AI analysis
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE collaboration_proposals 
                SET ai_compatibility_score = %s, ai_analysis = %s
                WHERE proposal_id = %s
            """, (
                compatibility_analysis['score'], compatibility_analysis['analysis'],
                proposal.proposal_id
            ))
            await session.commit()
        
        # Notify request creator
        # await notification_manager.send_proposal_notification(request_info[1], proposal)
        
        logger.info(f"Collaboration proposal submitted: {proposal.proposal_id}")
        
        return {
            "proposal_id": proposal.proposal_id,
            "compatibility_score": compatibility_analysis['score'],
            "message": "Proposal submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Submit collaboration proposal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit collaboration proposal"
        )


@router.get("/proposals/received", response_model=List[Dict[str, Any]])
async def get_received_proposals(
    request_id: Optional[str] = None,
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get proposals received for user's collaboration requests"""    try:
        query = """            SELECT cp.proposal_id, cp.collaboration_request_id, cp.proposer_id,
                   cp.proposal_message, cp.proposed_terms, cp.portfolio_samples,
                   cp.availability_details, cp.proposed_timeline, cp.budget_proposal,
                   cp.status, cp.ai_compatibility_score, cp.ai_analysis, cp.created_at,
                   cpr.stage_name, cpr.genres, cpr.skills, cpr.portfolio_links,
                   cr.title as request_title
            FROM collaboration_proposals cp
            JOIN collaboration_requests cr ON cp.collaboration_request_id = cr.request_id
            JOIN creator_profiles cpr ON cp.proposer_creator_id = cpr.creator_id
            WHERE cr.user_id = %s
        """        params = [user['user_id']]
        
        if request_id:
            query += " AND cp.collaboration_request_id = %s"
            params.append(request_id)
        
        if status:
            query += " AND cp.status = %s"
            params.append(status)
            
        query += " ORDER BY cp.ai_compatibility_score DESC, cp.created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            proposals = result.fetchall()
        
        proposal_list = []
        for proposal in proposals:
            proposal_list.append({
                "proposal_id": proposal[0],
                "collaboration_request_id": proposal[1],
                "proposer_id": proposal[2],
                "proposal_message": proposal[3],
                "proposed_terms": proposal[4],
                "portfolio_samples": proposal[5],
                "availability_details": proposal[6],
                "proposed_timeline": proposal[7],
                "budget_proposal": proposal[8],
                "status": proposal[9],
                "ai_compatibility_score": proposal[10],
                "ai_analysis": proposal[11],
                "created_at": proposal[12],
                "proposer_info": {
                    "stage_name": proposal[13],
                    "genres": proposal[14],
                    "skills": proposal[15],
                    "portfolio_links": proposal[16]
                },
                "request_title": proposal[17]
            })
        
        return proposal_list
        
    except Exception as e:
        logger.error(f"Get received proposals failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get received proposals"
        )


@router.post("/proposals/{proposal_id}/accept", response_model=Dict[str, str])
async def accept_collaboration_proposal(
    proposal_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Accept a collaboration proposal and create project"""    try:
        # Verify proposal ownership and status
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT cp.proposal_id, cp.collaboration_request_id, cp.proposer_id,
                       cp.proposed_terms, cp.proposed_timeline, cr.user_id, cr.title,
                       cr.description, cr.collaboration_type
                FROM collaboration_proposals cp
                JOIN collaboration_requests cr ON cp.collaboration_request_id = cr.request_id
                WHERE cp.proposal_id = %s AND cr.user_id = %s AND cp.status = 'pending'
            """, (proposal_id, user['user_id']))
            
            proposal_info = result.fetchone()
            if not proposal_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Proposal not found or cannot be accepted"
                )
        
        project_id = str(uuid.uuid4())
        
        # Create collaboration project
        project_data = {
            "title": proposal_info[6],
            "description": proposal_info[7],
            "participants": [user['user_id'], proposal_info[2]],
            "collaboration_type": proposal_info[8],
            "status": "active",
            "project_details": proposal_info[3],
            "milestones": [],
            "shared_resources": [],
            "communication_channels": {},
            "revenue_split": {}
        }
        
        async with database_manager.get_postgres_session() as session:
            # Accept proposal
            await session.execute("""                UPDATE collaboration_proposals 
                SET status = 'accepted', accepted_at = %s
                WHERE proposal_id = %s
            """, (datetime.utcnow(), proposal_id))
            
            # Reject other proposals for the same request
            await session.execute("""                UPDATE collaboration_proposals 
                SET status = 'rejected', rejected_at = %s
                WHERE collaboration_request_id = %s AND proposal_id != %s AND status = 'pending'
            """, (datetime.utcnow(), proposal_info[1], proposal_id))
            
            # Close collaboration request
            await session.execute("""                UPDATE collaboration_requests 
                SET status = 'closed', closed_at = %s
                WHERE request_id = %s
            """, (datetime.utcnow(), proposal_info[1]))
            
            # Create project
            await session.execute("""                INSERT INTO collaboration_projects (project_id, collaboration_request_id,
                                                  accepted_proposal_id, title, description,
                                                  participants, collaboration_type, status,
                                                  project_details, milestones, shared_resources,
                                                  communication_channels, revenue_split,
                                                  created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                project_id, proposal_info[1], proposal_id, project_data["title"],
                project_data["description"], project_data["participants"],
                project_data["collaboration_type"], project_data["status"],
                project_data["project_details"], project_data["milestones"],
                project_data["shared_resources"], project_data["communication_channels"],
                project_data["revenue_split"], datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Setup project workspace and communication channels
        background_tasks.add_task(_setup_collaboration_workspace, project_id, project_data)
        
        logger.info(f"Collaboration proposal accepted: {proposal_id}, project created: {project_id}")
        
        return {
            "project_id": project_id,
            "proposal_id": proposal_id,
            "message": "Proposal accepted and collaboration project created"
        }
        
    except Exception as e:
        logger.error(f"Accept collaboration proposal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept collaboration proposal"
        )


@router.get("/projects", response_model=List[Dict[str, Any]])
async def get_collaboration_projects(
    status: Optional[CollaborationStatus] = None,
    user: dict = Depends(get_current_user)
):
    """Get user's collaboration projects"""    try:
        query = """            SELECT project_id, title, description, participants, collaboration_type,
                   status, project_details, milestones, created_at, updated_at
            FROM collaboration_projects
            WHERE %s = ANY(participants)
        """        params = [user['user_id']]
        
        if status:
            query += " AND status = %s"
            params.append(status.value)
            
        query += " ORDER BY updated_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            projects = result.fetchall()
        
        project_list = []
        for project in projects:
            # Get participant details
            participant_details = []
            for participant_id in project[3]:
                participant_result = await session.execute("""                    SELECT cp.stage_name, cp.genres, cp.skills
                    FROM creator_profiles cp
                    WHERE cp.user_id = %s
                """, (participant_id,))
                participant_info = participant_result.fetchone()
                if participant_info:
                    participant_details.append({
                        "user_id": participant_id,
                        "stage_name": participant_info[0],
                        "genres": participant_info[1],
                        "skills": participant_info[2]
                    })
            
            project_list.append({
                "project_id": project[0],
                "title": project[1],
                "description": project[2],
                "participants": participant_details,
                "collaboration_type": project[4],
                "status": project[5],
                "project_details": project[6],
                "milestones": project[7],
                "created_at": project[8],
                "updated_at": project[9]
            })
        
        return project_list
        
    except Exception as e:
        logger.error(f"Get collaboration projects failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collaboration projects"
        )


@router.post("/reviews", response_model=Dict[str, str])
async def submit_collaboration_review(
    review: CollaborationReview,
    user: dict = Depends(get_current_user)
):
    """Submit a review for a collaboration partner"""    try:
        # Verify project participation and completion
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT project_id, status, participants
                FROM collaboration_projects
                WHERE project_id = %s AND %s = ANY(participants)
                  AND status IN ('completed', 'cancelled')
            """, (review.project_id, user['user_id']))
            
            project_info = result.fetchone()
            if not project_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or not eligible for review"
                )
            
            # Verify reviewed user was a participant
            if review.reviewed_user_id not in project_info[2]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reviewed user was not a participant in this project"
                )
            
            # Check if review already exists
            result = await session.execute("""                SELECT review_id FROM collaboration_reviews
                WHERE project_id = %s AND reviewer_id = %s AND reviewed_user_id = %s
            """, (review.project_id, user['user_id'], review.reviewed_user_id))
            
            if result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Review already exists for this collaboration"
                )
        
        # Create review
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO collaboration_reviews (review_id, project_id, reviewer_id,
                                                 reviewed_user_id, rating, review_text,
                                                 collaboration_aspects, would_collaborate_again,
                                                 created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                review.review_id, review.project_id, user['user_id'], review.reviewed_user_id,
                review.rating, review.review_text, review.collaboration_aspects,
                review.would_collaborate_again, datetime.utcnow()
            ))
            await session.commit()
        
        # Update user's collaboration reputation
        await _update_collaboration_reputation(review.reviewed_user_id)
        
        logger.info(f"Collaboration review submitted: {review.review_id}")
        
        return {
            "review_id": review.review_id,
            "message": "Collaboration review submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Submit collaboration review failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit collaboration review"
        )


@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_collaboration_recommendations(
    collaboration_type: Optional[CollaborationType] = None,
    genres: Optional[List[str]] = None,
    limit: int = Field(default=10, ge=1, le=50),
    user: dict = Depends(get_current_user)
):
    """Get AI-powered collaboration recommendations"""    try:
        # Get user's creator profile
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT creator_id, genres, skills, collaboration_preferences
                FROM creator_profiles
                WHERE user_id = %s
            """, (user['user_id'],))
            
            user_profile = result.fetchone()
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creator profile required for recommendations"
                )
        
        # Generate AI recommendations
        recommendations = await matching_engine.get_collaboration_recommendations(
            user_profile[0], collaboration_type, genres, limit
        )
        
        # Enrich recommendations with creator details
        enriched_recommendations = []
        async with database_manager.get_postgres_session() as session:
            for rec in recommendations:
                result = await session.execute("""                    SELECT cp.stage_name, cp.bio, cp.genres, cp.skills, cp.portfolio_links,
                           cp.social_media, cr.avg_rating, cr.total_collaborations
                    FROM creator_profiles cp
                    LEFT JOIN collaboration_reputations cr ON cp.creator_id = cr.creator_id
                    WHERE cp.creator_id = %s
                """, (rec['creator_id'],))
                
                creator_info = result.fetchone()
                if creator_info:
                    enriched_recommendations.append({
                        "creator_id": rec['creator_id'],
                        "compatibility_score": rec['compatibility_score'],
                        "match_reasons": rec['match_reasons'],
                        "collaboration_potential": rec['collaboration_potential'],
                        "creator_info": {
                            "stage_name": creator_info[0],
                            "bio": creator_info[1],
                            "genres": creator_info[2],
                            "skills": creator_info[3],
                            "portfolio_links": creator_info[4],
                            "social_media": creator_info[5],
                            "reputation": {
                                "avg_rating": float(creator_info[6]) if creator_info[6] else 0.0,
                                "total_collaborations": creator_info[7] or 0
                            }
                        }
                    })
        
        return enriched_recommendations
        
    except Exception as e:
        logger.error(f"Get collaboration recommendations failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collaboration recommendations"
        )


# Background task functions
async def _find_collaboration_matches(request_id: str, creator_id: str):
    """Find AI-powered collaboration matches for a request"""    try:
        # Get request details
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT collaboration_type, genres, required_skills, experience_level
                FROM collaboration_requests
                WHERE request_id = %s
            """, (request_id,))
            
            request_details = result.fetchone()
            if not request_details:
                return
        
        # Find potential matches using AI
        matches = await matching_engine.find_collaboration_matches(
            request_id, creator_id, request_details
        )
        
        # Store matches in database
        async with database_manager.get_postgres_session() as session:
            for match in matches:
                match_id = str(uuid.uuid4())
                await session.execute("""                    INSERT INTO collaboration_matches (match_id, requester_id, matched_creator_id,
                                                     collaboration_request_id, compatibility_score,
                                                     match_reasons, shared_genres, complementary_skills,
                                                     estimated_success_rate, ai_recommendation, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    match_id, creator_id, match['creator_id'], request_id,
                    match['compatibility_score'], match['match_reasons'],
                    match['shared_genres'], match['complementary_skills'],
                    match['estimated_success_rate'], match['ai_recommendation'],
                    datetime.utcnow()
                ))
            await session.commit()
        
        logger.info(f"Found {len(matches)} collaboration matches for request {request_id}")
        
    except Exception as e:
        logger.error(f"Find collaboration matches failed: {e}")


async def _setup_collaboration_workspace(project_id: str, project_data: Dict[str, Any]):
    """Setup collaboration workspace and communication channels"""    try:
        # Create communication channels (Slack, Discord, etc.)
        workspace_setup = await collaboration_engine.setup_project_workspace(
            project_id, project_data
        )
        
        # Update project with workspace details
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE collaboration_projects 
                SET communication_channels = %s, workspace_setup = %s
                WHERE project_id = %s
            """, (workspace_setup['channels'], workspace_setup, project_id))
            await session.commit()
        
        logger.info(f"Collaboration workspace setup completed for project {project_id}")
        
    except Exception as e:
        logger.error(f"Setup collaboration workspace failed: {e}")


async def _update_collaboration_reputation(user_id: str):
    """Update user's collaboration reputation based on reviews"""    try:
        async with database_manager.get_postgres_session() as session:
            # Calculate reputation metrics
            result = await session.execute("""                SELECT AVG(rating) as avg_rating, COUNT(*) as total_reviews,
                       AVG(CASE WHEN would_collaborate_again THEN 1 ELSE 0 END) as collaboration_willingness
                FROM collaboration_reviews
                WHERE reviewed_user_id = %s
            """, (user_id,))
            
            reputation_data = result.fetchone()
            if reputation_data and reputation_data[1] > 0:
                # Update or create reputation record
                await session.execute("""                    INSERT INTO collaboration_reputations (user_id, avg_rating, total_reviews,
                                                         collaboration_willingness, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        avg_rating = EXCLUDED.avg_rating,
                        total_reviews = EXCLUDED.total_reviews,
                        collaboration_willingness = EXCLUDED.collaboration_willingness,
                        updated_at = EXCLUDED.updated_at
                """, (
                    user_id, reputation_data[0], reputation_data[1],
                    reputation_data[2], datetime.utcnow()
                ))
                await session.commit()
        
        logger.debug(f"Collaboration reputation updated for user {user_id}")
        
    except Exception as e:
        logger.error(f"Update collaboration reputation failed: {e}")