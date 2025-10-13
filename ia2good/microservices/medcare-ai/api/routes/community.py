"""
Community Forum Routes
Anonymous medical case discussions and second opinions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional, List
import logging

from models.community import (
    CommunityPostCreate, CommunityPost, PostWithResponses,
    CommunityResponseCreate, CommunityResponse, VoteResponse,
    AuthorType, PostType, PostStatus
)
from services.community_service import CommunityForumService
from utils.database import get_db
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/medcare/community", tags=["Community Forum"])
logger = logging.getLogger(__name__)


@router.post("/posts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_community_post(
    post_data: CommunityPostCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create anonymous community post
    
    Types:
    - case_discussion: Share a medical case for discussion
    - second_opinion: Ask for second opinion on diagnosis
    - medical_advice: Seek general medical advice
    - document_review: Ask community to review medical documents
    
    All posts are anonymous by default. Your identity is protected.
    Content is automatically translated to multiple languages.
    
    Example use cases:
    - Patient wants second opinion on X-ray results
    - Doctor has difficult case and wants peer consultation
    - Patient needs advice on managing chronic condition
    - Specialist wants to discuss treatment options
    """
    
    try:
        service = CommunityForumService(db)
        
        post = await service.create_post(
            author_id=post_data.author_id,
            author_type=post_data.author_type.value,
            post_type=post_data.post_type.value,
            title=post_data.title,
            content=post_data.content,
            language=post_data.language,
            related_document_id=post_data.related_document_id,
            is_anonymous=post_data.is_anonymous,
            tags=post_data.tags
        )
        
        return {
            "success": True,
            "post_id": post['id'],
            "anonymous_name": post['anonymous_display_name'],
            "message": "Post created successfully",
            "post_url": f"/medcare/community/posts/{post['id']}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Post creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating post: {str(e)}"
        )


@router.get("/posts/{post_id}", response_model=PostWithResponses)
async def get_post(
    post_id: UUID,
    viewer_language: str = Query("en", description="Preferred language for translations"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get community post with all responses
    
    Content is automatically translated to viewer's preferred language
    """
    
    try:
        service = CommunityForumService(db)
        
        result = await service.get_post_with_responses(
            post_id,
            viewer_language,
            current_user['id']
        )
        
        return PostWithResponses(**result)
        
    except Exception as e:
        logger.error(f"Post retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found"
        )


@router.post("/posts/{post_id}/responses", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_response(
    post_id: UUID,
    response_data: CommunityResponseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add response to community post
    
    Share your medical expertise or experience to help others.
    Responses are anonymous by default.
    
    Helpful responses get upvoted by the community.
    """
    
    try:
        service = CommunityForumService(db)
        
        response = await service.add_response(
            post_id=post_id,
            author_id=response_data.author_id,
            author_type=response_data.author_type.value,
            content=response_data.content,
            language=response_data.language,
            is_anonymous=response_data.is_anonymous
        )
        
        return {
            "success": True,
            "response_id": response['id'],
            "anonymous_name": response['anonymous_display_name'],
            "message": "Response added successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Response creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding response: {str(e)}"
        )


@router.post("/responses/{response_id}/vote", status_code=status.HTTP_200_OK)
async def vote_response_helpful(
    response_id: UUID,
    vote_data: VoteResponse,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vote a response as helpful
    
    Help the community identify the most useful medical advice
    """
    
    try:
        service = CommunityForumService(db)
        
        success = await service.vote_helpful(response_id, vote_data.voter_id)
        
        if success:
            return {
                "success": True,
                "message": "Vote recorded"
            }
        else:
            return {
                "success": False,
                "message": "You have already voted on this response"
            }
        
    except Exception as e:
        logger.error(f"Voting error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording vote: {str(e)}"
        )


@router.get("/posts", response_model=List[dict])
async def search_posts(
    query: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    post_type: Optional[PostType] = Query(None, description="Filter by post type"),
    language: str = Query("en", description="Preferred language"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search community posts
    
    Filter by:
    - Text query (searches in title and content)
    - Tags (medical specialties, conditions, etc.)
    - Post type
    
    Results are translated to your preferred language
    """
    
    try:
        service = CommunityForumService(db)
        
        tag_list = tags.split(',') if tags else None
        
        posts = await service.search_posts(
            query=query,
            tags=tag_list,
            post_type=post_type.value if post_type else None,
            language=language,
            limit=limit,
            offset=offset
        )
        
        return posts
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching posts: {str(e)}"
        )


@router.get("/trending", response_model=List[dict])
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get trending community posts
    
    Based on:
    - Recent activity
    - Number of responses
    - Helpful votes
    - Views
    """
    
    try:
        service = CommunityForumService(db)
        
        trending = await service.get_trending_posts(limit)
        
        return trending
        
    except Exception as e:
        logger.error(f"Trending posts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trending posts: {str(e)}"
        )


@router.post("/flag", status_code=status.HTTP_200_OK)
async def flag_inappropriate_content(
    content_id: UUID,
    content_type: str,
    reason: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Flag inappropriate content for moderation
    
    Reasons:
    - spam: Spam or advertising
    - offensive: Offensive language
    - misinformation: Medical misinformation
    - personal_info: Contains personal information
    - other: Other reason (specify in reason field)
    """
    
    try:
        service = CommunityForumService(db)
        
        flag = await service.flag_content(
            content_id,
            content_type,
            current_user['id'],
            reason
        )
        
        return {
            "success": True,
            "message": "Content flagged for review",
            "flag_id": flag['id']
        }
        
    except Exception as e:
        logger.error(f"Flagging error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error flagging content: {str(e)}"
        )
