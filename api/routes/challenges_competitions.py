"""
🎯 Challenges & Competitions API Routes - IA Influencer Agent Platform Enterprise
==================================================================================
Module: api/routes/challenges_competitions.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge & Competition API - Production-Ready
Responsibility: API endpoints for creative, technical, and global challenges/competitions
==========================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Challenge Discovery → Participation Registration → Progress Tracking → 
Submission Evaluation → Reward Distribution → Community Engagement

API ARCHITECTURE:
Challenge Management → Competition Engine → Evaluation System → 
Reward Calculator → Analytics Integration → Performance Optimization
"""

from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from enum import Enum
import logging

from ...business.engagement.challenge_engine import (
    ChallengeEngine, 
    ChallengeType, 
    ChallengeDifficulty,
    ChallengeStatus,
    ParticipationStatus,
    ContentFormat,
    get_challenge_engine,
    create_challenge_from_template,
    register_for_challenge
)
from ...core.challenges.challenge_engine import ChallengeConfiguration
from ...core.challenges.competition_manager import CompetitionManager, CompetitionConfiguration
from ..dependencies import get_current_user, verify_permissions

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/challenges-competitions", tags=["Challenges & Competitions"])

# Request/Response Models
class ChallengeTypeFilter(str, Enum):
    ALL = "all"
    CREATIVE_MONTHLY = "creative_monthly"
    TECHNICAL_SEO = "technical_seo" 
    TECHNICAL_REVENUE = "technical_revenue"
    GLOBAL_COMPETITION = "global_competition"
    SPECIAL_EVENT = "special_event"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"

class CreateChallengeRequest(BaseModel):
    template_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty = ChallengeDifficulty.INTERMEDIATE
    duration_days: int = Field(default=30, ge=1, le=365)
    content_formats: List[ContentFormat] = Field(default_factory=list)
    max_participants: Optional[int] = Field(default=None, ge=1)
    custom_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('title')
    def validate_title(cls, v, values):
        if not values.get('template_name') and (not v or len(v.strip()) < 5):
            raise ValueError('Title must be at least 5 characters when not using template')
        return v

class ParticipationRequest(BaseModel):
    challenge_id: str = Field(..., description="Challenge ID to participate in")
    team_id: Optional[str] = Field(None, description="Team ID if participating as team")
    registration_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProgressUpdateRequest(BaseModel):
    challenge_id: str
    progress_data: Dict[str, Any] = Field(..., description="Progress metrics and data")
    
    class Config:
        schema_extra = {
            "example": {
                "challenge_id": "challenge_123",
                "progress_data": {
                    "seo_ranking_improvement": 45.5,
                    "organic_traffic_growth": 78.2,
                    "engagement_rate": 12.5,
                    "revenue_increase_percentage": 42.0
                }
            }
        }

class SubmissionRequest(BaseModel):
    challenge_id: str
    submission_data: Dict[str, Any] = Field(..., description="Submission content and metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "challenge_id": "challenge_123",
                "submission_data": {
                    "content_url": "https://example.com/content",
                    "title": "My Amazing Creation",
                    "description": "This is my submission description",
                    "tags": ["creative", "innovative"],
                    "techniques_used": ["ai_enhancement", "professional_mixing"],
                    "metrics": {
                        "quality_score": 85.5,
                        "creativity_score": 92.0
                    }
                }
            }
        }

class ChallengeResponse(BaseModel):
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    status: ChallengeStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    participant_count: int
    submission_count: int
    max_participants: Optional[int]
    is_participating: bool = False
    user_progress: Optional[float] = None
    time_remaining: Optional[str] = None
    rewards: List[Dict[str, Any]] = Field(default_factory=list)

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    score: float
    completion_percentage: float
    milestones_achieved: int
    submission_title: Optional[str] = None
    awards: List[str] = Field(default_factory=list)

class ChallengeStatsResponse(BaseModel):
    challenge_id: str
    title: str
    status: ChallengeStatus
    is_active: bool
    time_remaining: Optional[float]
    participants: Dict[str, Any]
    performance: Dict[str, Any]
    timing: Dict[str, Any]

# API Endpoints

@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    challenge_type: ChallengeTypeFilter = Query(ChallengeTypeFilter.ALL, description="Filter by challenge type"),
    difficulty: Optional[ChallengeDifficulty] = Query(None, description="Filter by difficulty"),
    status: Optional[ChallengeStatus] = Query(None, description="Filter by status"), 
    limit: int = Query(20, ge=1, le=100, description="Number of challenges to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of challenges with filtering options.
    
    Supports filtering by:
    - Challenge type (creative_monthly, technical_seo, technical_revenue, global_competition, etc.)
    - Difficulty level
    - Status (active, upcoming, completed)
    """
    try:
        engine = await get_challenge_engine()
        
        # Convert filter to actual challenge type
        type_filter = None
        if challenge_type != ChallengeTypeFilter.ALL:
            type_filter = ChallengeType(challenge_type.value)
        
        # Get challenges with filters
        challenges = await engine.get_active_challenges(
            user_id=current_user["user_id"],
            challenge_type=type_filter,
            difficulty=difficulty
        )
        
        # Convert to response format
        response_challenges = []
        for challenge in challenges[offset:offset + limit]:
            # Get user participation info
            user_challenges = await engine.get_user_challenges(current_user["user_id"])
            user_participation = next(
                (uc[1] for uc in user_challenges if uc[0].challenge_id == challenge.challenge_id), 
                None
            )
            
            # Calculate time remaining
            time_remaining = None
            if challenge.get_time_remaining():
                time_remaining = str(challenge.get_time_remaining())
            
            response_challenges.append(ChallengeResponse(
                challenge_id=challenge.challenge_id,
                title=challenge.title,
                description=challenge.description,
                challenge_type=challenge.challenge_type,
                difficulty=challenge.difficulty,
                status=challenge.status,
                start_date=challenge.start_date,
                end_date=challenge.end_date,
                participant_count=challenge.participant_count,
                submission_count=challenge.submission_count,
                max_participants=challenge.max_participants,
                is_participating=user_participation is not None,
                user_progress=user_participation.progress_percentage if user_participation else None,
                time_remaining=time_remaining,
                rewards=[reward.__dict__ for reward in challenge.completion_rewards]
            ))
        
        return response_challenges
        
    except Exception as e:
        logger.error(f"Failed to get challenges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve challenges")

@router.post("/create", response_model=ChallengeResponse)
async def create_challenge(
    request: CreateChallengeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    _: None = Depends(verify_permissions("challenge:create"))
):
    """
    Create a new challenge from template or custom parameters.
    
    Supports creating:
    - Monthly creative challenges with rewards
    - Technical SEO optimization challenges
    - Revenue optimization challenges  
    - Global competitions and special events
    """
    try:
        engine = await get_challenge_engine()
        
        # Prepare custom parameters
        custom_params = request.custom_params.copy()
        if request.title:
            custom_params["title"] = request.title
        if request.description:
            custom_params["description"] = request.description
        
        custom_params.update({
            "challenge_type": request.challenge_type,
            "difficulty": request.difficulty,
            "duration_days": request.duration_days,
            "content_formats": request.content_formats,
            "max_participants": request.max_participants,
            "created_by": current_user["user_id"]
        })
        
        # Create challenge
        challenge = await engine.create_challenge(
            template_name=request.template_name,
            custom_params=custom_params
        )
        
        # Calculate time remaining
        time_remaining = None
        if challenge.get_time_remaining():
            time_remaining = str(challenge.get_time_remaining())
        
        return ChallengeResponse(
            challenge_id=challenge.challenge_id,
            title=challenge.title,
            description=challenge.description,
            challenge_type=challenge.challenge_type,
            difficulty=challenge.difficulty,
            status=challenge.status,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            participant_count=challenge.participant_count,
            submission_count=challenge.submission_count,
            max_participants=challenge.max_participants,
            time_remaining=time_remaining,
            rewards=[reward.__dict__ for reward in challenge.completion_rewards]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create challenge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create challenge")

@router.post("/participate")
async def participate_in_challenge(
    request: ParticipationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Register user for challenge participation.
    """
    try:
        participation = await register_for_challenge(
            challenge_id=request.challenge_id,
            user_id=current_user["user_id"],
            team_id=request.team_id
        )
        
        return {
            "success": True,
            "participation_id": participation.participation_id,
            "challenge_id": participation.challenge_id,
            "status": participation.status,
            "registered_at": participation.registered_at
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register for challenge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register for challenge")

@router.put("/progress")
async def update_challenge_progress(
    request: ProgressUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user progress in a challenge.
    
    Supports progress tracking for:
    - SEO improvement metrics (ranking_improvement, traffic_growth, etc.)
    - Revenue optimization metrics (revenue_increase, monetization_rate, etc.)
    - Creative challenge metrics (quality_score, engagement_rate, etc.)
    - Global competition metrics (global_reach, international_engagement, etc.)
    """
    try:
        engine = await get_challenge_engine()
        
        success = await engine.update_challenge_progress(
            challenge_id=request.challenge_id,
            user_id=current_user["user_id"],
            progress_data=request.progress_data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update progress")
        
        return {"success": True, "message": "Progress updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")

@router.post("/submit")
async def submit_challenge_entry(
    request: SubmissionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submit an entry for a challenge.
    """
    try:
        engine = await get_challenge_engine()
        
        success = await engine.submit_challenge_entry(
            challenge_id=request.challenge_id,
            user_id=current_user["user_id"],
            submission_data=request.submission_data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to submit entry")
        
        return {"success": True, "message": "Entry submitted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to submit entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit entry")

@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge_details(
    challenge_id: str = Path(..., description="Challenge ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information about a specific challenge.
    """
    try:
        engine = await get_challenge_engine()
        
        # Find challenge in active challenges
        challenges = await engine.get_active_challenges(user_id=current_user["user_id"])
        challenge = next((c for c in challenges if c.challenge_id == challenge_id), None)
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Get user participation info
        user_challenges = await engine.get_user_challenges(current_user["user_id"])
        user_participation = next(
            (uc[1] for uc in user_challenges if uc[0].challenge_id == challenge_id), 
            None
        )
        
        # Calculate time remaining
        time_remaining = None
        if challenge.get_time_remaining():
            time_remaining = str(challenge.get_time_remaining())
        
        return ChallengeResponse(
            challenge_id=challenge.challenge_id,
            title=challenge.title,
            description=challenge.description,
            challenge_type=challenge.challenge_type,
            difficulty=challenge.difficulty,
            status=challenge.status,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            participant_count=challenge.participant_count,
            submission_count=challenge.submission_count,
            max_participants=challenge.max_participants,
            is_participating=user_participation is not None,
            user_progress=user_participation.progress_percentage if user_participation else None,
            time_remaining=time_remaining,
            rewards=[reward.__dict__ for reward in challenge.completion_rewards]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get challenge details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve challenge details")

@router.get("/{challenge_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_challenge_leaderboard(
    challenge_id: str = Path(..., description="Challenge ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get challenge leaderboard with rankings.
    """
    try:
        engine = await get_challenge_engine()
        
        leaderboard = await engine.get_challenge_leaderboard(challenge_id, limit=limit)
        
        response_entries = []
        for participation, rank in leaderboard:
            response_entries.append(LeaderboardEntry(
                rank=rank,
                user_id=participation.user_id,
                username=f"User_{participation.user_id[:8]}", # Would fetch actual username
                score=participation.total_score,
                completion_percentage=participation.progress_percentage,
                milestones_achieved=len(participation.milestones_completed),
                submission_title=participation.submission_data.get("title"),
                awards=[]  # Would fetch from rewards_earned
            ))
        
        return response_entries
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve leaderboard")

@router.get("/{challenge_id}/stats", response_model=ChallengeStatsResponse)
async def get_challenge_statistics(
    challenge_id: str = Path(..., description="Challenge ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive challenge statistics.
    """
    try:
        engine = await get_challenge_engine()
        
        stats = await engine.get_challenge_statistics(challenge_id)
        
        return ChallengeStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get challenge statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve challenge statistics")

@router.get("/my/challenges", response_model=List[ChallengeResponse])
async def get_my_challenges(
    status_filter: Optional[ParticipationStatus] = Query(None, description="Filter by participation status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's challenge participation history.
    """
    try:
        engine = await get_challenge_engine()
        
        user_challenges = await engine.get_user_challenges(
            user_id=current_user["user_id"],
            status_filter=status_filter
        )
        
        response_challenges = []
        for challenge, participation in user_challenges[offset:offset + limit]:
            # Calculate time remaining
            time_remaining = None
            if challenge.get_time_remaining():
                time_remaining = str(challenge.get_time_remaining())
            
            response_challenges.append(ChallengeResponse(
                challenge_id=challenge.challenge_id,
                title=challenge.title,
                description=challenge.description,
                challenge_type=challenge.challenge_type,
                difficulty=challenge.difficulty,
                status=challenge.status,
                start_date=challenge.start_date,
                end_date=challenge.end_date,
                participant_count=challenge.participant_count,
                submission_count=challenge.submission_count,
                max_participants=challenge.max_participants,
                is_participating=True,
                user_progress=participation.progress_percentage,
                time_remaining=time_remaining,
                rewards=[reward.__dict__ for reward in participation.rewards_earned]
            ))
        
        return response_challenges
        
    except Exception as e:
        logger.error(f"Failed to get user challenges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user challenges")

@router.get("/templates/list")
async def get_challenge_templates(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of available challenge templates.
    """
    try:
        engine = await get_challenge_engine()
        
        # Get template names and descriptions
        templates = {
            # Creative Monthly Challenges
            "monthly_creative_masterpiece": {
                "name": "Monthly Creative Masterpiece Challenge", 
                "category": "Creative Monthly",
                "description": "Monthly creative challenge with premium rewards",
                "difficulty": "intermediate",
                "duration": "30 days"
            },
            "artistic_innovation_monthly": {
                "name": "Artistic Innovation Monthly",
                "category": "Creative Monthly", 
                "description": "Monthly AI-powered artistic innovation competition",
                "difficulty": "advanced",
                "duration": "31 days"
            },
            
            # Technical Challenges
            "seo_optimization_master": {
                "name": "SEO Optimization Master Challenge",
                "category": "Technical SEO",
                "description": "Optimize content for maximum search visibility",
                "difficulty": "advanced", 
                "duration": "30 days"
            },
            "revenue_optimization_champion": {
                "name": "Revenue Optimization Champion",
                "category": "Technical Revenue",
                "description": "Maximize content monetization and revenue",
                "difficulty": "expert",
                "duration": "30 days"
            },
            "performance_analytics_master": {
                "name": "Performance Analytics Master",
                "category": "Technical Analytics",
                "description": "Master content analytics and performance optimization",
                "difficulty": "advanced",
                "duration": "21 days"
            },
            
            # Global Competitions
            "global_creative_championship": {
                "name": "Global Creative Championship",
                "category": "Global Competition",
                "description": "Ultimate global creative competition with massive prizes",
                "difficulty": "expert",
                "duration": "45 days"
            },
            "world_collaboration_summit": {
                "name": "World Collaboration Summit", 
                "category": "Global Collaboration",
                "description": "Global collaboration event across continents",
                "difficulty": "master",
                "duration": "60 days"
            },
            "ainflue_anniversary_spectacular": {
                "name": "Ainflue Anniversary Spectacular",
                "category": "Special Event",
                "description": "Annual global celebration with extraordinary prizes",
                "difficulty": "master",
                "duration": "30 days"
            }
        }
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Failed to get templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")