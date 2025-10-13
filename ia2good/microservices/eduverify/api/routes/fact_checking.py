"""
Fact-Checking API Routes for EduVerify
Verify facts and claims with AI
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.fact_check import (
    FactCheck,
    FactCheckRequest,
    FactCheckList,
)
from services.fact_checker import FactCheckerService
from database import get_db, FactCheckModel
import uuid as uuid_lib
from datetime import datetime

router = APIRouter(prefix="/eduverify/fact-check", tags=["eduverify-fact-checking"])


def get_current_user():
    """Get current authenticated user - Simple UUID for now"""
    class User:
        def __init__(self):
            self.id = uuid_lib.uuid4()
    return User()


@router.post("", response_model=FactCheck, status_code=201)
async def check_fact(
    request: FactCheckRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify a factual claim using AI and reliable sources
    
    Process:
    1. Extract key claim from text
    2. Search reliable sources (Wikipedia, academic DBs, news)
    3. Rank sources by credibility
    4. Use LLM to analyze claim vs sources
    5. Generate verdict (true/false/unverified/etc.)
    6. Calculate confidence score
    7. Provide detailed explanation
    8. Include source references
    
    Target Performance:
    - Precision: >92%
    - Latency: <3s for standard checks
    - Sources: Minimum 2 reliable sources
    
    Verdict Levels:
    - TRUE: Claim is accurate
    - MOSTLY_TRUE: Claim is mostly accurate with minor issues
    - HALF_TRUE: Claim has both accurate and inaccurate elements
    - MOSTLY_FALSE: Claim is mostly inaccurate
    - FALSE: Claim is completely false
    - UNVERIFIED: Not enough reliable sources to verify
    
    Returns:
        Fact-check result with verdict, confidence, sources, and explanation
    """
    try:
        checker = FactCheckerService()
        
        # REAL FACT-CHECKING - No mock!
        result = await checker.check_fact(
            claim=request.claim,
            context=request.context or "",
            language=request.language
        )
        
        # SAVE TO DATABASE
        fact_check_record = FactCheckModel(
            id=result["id"],
            content_id=request.content_id,
            user_id=current_user.id,
            claim=request.claim,
            verification_result=result["verdict"],  # Map to correct column name
            confidence=result["confidence_score"],  # Map to correct column name
            verification_text=result["explanation"],  # Map to correct column name
            sources=result["sources"],  # JSON field
            num_sources=len(result["sources"]),
            context=request.context,
            language=request.language,
            created_at=datetime.utcnow()
        )
        
        db.add(fact_check_record)
        db.commit()
        db.refresh(fact_check_record)
        
        # Map verdict to enum format
        verdict_map = {
            "verified": "true",
            "partially_verified": "half_true",
            "false": "false",
            "unverifiable": "unverified"
        }
        
        # Return FactCheck model
        return FactCheck(
            id=fact_check_record.id,
            content_id=fact_check_record.content_id,
            user_id=fact_check_record.user_id,
            claim=fact_check_record.claim,
            verdict=verdict_map.get(fact_check_record.verification_result, "unverified"),
            confidence=fact_check_record.confidence,
            explanation=fact_check_record.verification_text,
            sources=[{
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "credibility_score": s.get("credibility_score", 0.5),
                "excerpt": s.get("snippet", "")
            } for s in result["sources"]],
            context=fact_check_record.context,
            ai_reasoning=result.get("explanation", fact_check_record.verification_text),
            created_at=fact_check_record.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check fact: {str(e)}")


@router.get("/{fact_check_id}", response_model=FactCheck)
async def get_fact_check(
    fact_check_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get fact-check result details
    
    Returns:
        - Claim and verdict
        - Confidence score
        - All sources with credibility scores
        - Detailed explanation
        - AI reasoning process
        - Human verification status
    """
    try:
        # TODO: Fetch from database
        raise HTTPException(status_code=404, detail="Fact-check not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch fact-check: {str(e)}")


@router.get("", response_model=FactCheckList)
async def list_fact_checks(
    content_id: Optional[UUID] = None,
    verdict: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List fact-check history
    
    Filters:
    - content_id: Filter by content
    - verdict: Filter by verdict type
    
    Pagination:
    - page: Page number (default 1)
    - per_page: Items per page (default 20, max 100)
    """
    try:
        # TODO: Query database with filters
        
        return FactCheckList(
            items=[],
            total=0,
            page=page,
            per_page=per_page,
            pages=0,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list fact-checks: {str(e)}")


@router.post("/batch", status_code=201)
async def batch_fact_check(
    claims: list[str],
    context: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check multiple facts in batch
    
    Useful for:
    - Fact-checking entire articles
    - Live lecture transcripts
    - Educational content review
    
    Process:
    1. Extract all claims from list
    2. Check each claim concurrently
    3. Return results array in same order
    
    Returns:
        Array of fact-check results
    """
    try:
        checker = FactCheckerService()
        
        # TODO: Batch process claims
        # results = await checker.batch_check(claims, context)
        
        return {
            "total_claims": len(claims),
            "results": [],
            "processing_time_seconds": 0,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch check facts: {str(e)}")


@router.put("/{fact_check_id}/verify", response_model=FactCheck)
async def human_verify_fact_check(
    fact_check_id: UUID,
    is_correct: bool,
    notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add human verification to AI fact-check
    
    Used for:
    - Quality control
    - Training data improvement
    - Dispute resolution
    
    Parameters:
    - is_correct: Whether AI verdict was correct
    - notes: Optional expert notes
    """
    try:
        # TODO: Update fact-check with human verification
        
        raise HTTPException(status_code=404, detail="Fact-check not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify fact-check: {str(e)}")
