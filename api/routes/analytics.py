"""Analytics API Routes
Content analytics, performance metrics, and insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.logging import logger


# Pydantic models
class AnalyticsOverview(BaseModel):
    total_content: int
    protected_content: int
    total_violations: int
    pending_violations: int
    total_views: int
    engagement_rate: float


class ContentAnalytics(BaseModel):
    content_id: str
    title: str
    content_type: str
    quality_score: float
    engagement_score: float
    violations_count: int
    last_analyzed: Optional[datetime]


class PlatformAnalytics(BaseModel):
    platform: str
    content_count: int
    violations_count: int
    avg_similarity_score: float


# Router setup
router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get analytics overview for user"""    try:
        user_id = current_user["user_id"]
        
        async with database_manager.get_postgres_session() as session:
            # Get content statistics
            content_result = await session.execute(
                "SELECT COUNT(*) FROM content WHERE user_id = %s AND active = true",
                (user_id,)
            )
            total_content = content_result.fetchone()[0]
            
            # Get protected content count
            protected_result = await session.execute(
                """                SELECT COUNT(DISTINCT content_id) 
                FROM content_monitoring 
                WHERE user_id = %s AND active = true
                """,
                (user_id,)
            )
            protected_content = protected_result.fetchone()[0]
            
            # Get violations statistics
            violations_result = await session.execute(
                "SELECT COUNT(*), COUNT(CASE WHEN status = 'pending_review' THEN 1 END) FROM protection_violations WHERE user_id = %s",
                (user_id,)
            )
            violations_row = violations_result.fetchone()
            total_violations = violations_row[0]
            pending_violations = violations_row[1] or 0
        
        return AnalyticsOverview(
            total_content=total_content,
            protected_content=protected_content,
            total_violations=total_violations,
            pending_violations=pending_violations,
            total_views=0,  # Placeholder
            engagement_rate=0.0  # Placeholder
        )
        
    except Exception as e:
        logger.error(f"Get analytics overview failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics overview"
        )


@router.get("/content", response_model=List[ContentAnalytics])
async def get_content_analytics(
    limit: int = 20,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get detailed content analytics"""    try:
        user_id = current_user["user_id"]
        
        content_analytics = []
        
        # Get content with basic info
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """                SELECT c.id, c.title, c.content_type, 
                       COUNT(pv.id) as violations_count
                FROM content c
                LEFT JOIN protection_violations pv ON c.id = pv.original_content_id
                WHERE c.user_id = %s AND c.active = true
                GROUP BY c.id, c.title, c.content_type
                ORDER BY c.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset)
            )
            
            for row in result.fetchall():
                # Get analysis data from MongoDB
                analysis_collection = await database_manager.get_mongodb_collection("content_analysis")
                analysis_doc = await analysis_collection.find_one({
                    "content_id": row[0],
                    "user_id": user_id
                }, sort=[("created_at", -1)])
                
                quality_score = 0.0
                engagement_score = 0.0
                last_analyzed = None
                
                if analysis_doc:
                    analysis_result = analysis_doc.get("analysis_result", {})
                    quality_analysis = analysis_result.get("quality_analysis", {})
                    
                    quality_score = quality_analysis.get("engagement_score", 0.0)
                    engagement_score = quality_analysis.get("viral_potential", 0.0)
                    last_analyzed = analysis_doc.get("created_at")
                
                content_analytics.append(ContentAnalytics(
                    content_id=row[0],
                    title=row[1],
                    content_type=row[2],
                    quality_score=quality_score,
                    engagement_score=engagement_score,
                    violations_count=row[3],
                    last_analyzed=last_analyzed
                ))
        
        return content_analytics
        
    except Exception as e:
        logger.error(f"Get content analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content analytics"
        )


@router.get("/platforms", response_model=List[PlatformAnalytics])
async def get_platform_analytics(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get platform-specific analytics"""    try:
        user_id = current_user["user_id"]
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """                SELECT 
                    pv.platform,
                    COUNT(DISTINCT pv.original_content_id) as content_count,
                    COUNT(pv.id) as violations_count,
                    AVG(pv.similarity_score) as avg_similarity_score
                FROM protection_violations pv
                WHERE pv.user_id = %s
                GROUP BY pv.platform
                ORDER BY violations_count DESC
                """,
                (user_id,)
            )
            
            platform_analytics = []
            for row in result.fetchall():
                platform_analytics.append(PlatformAnalytics(
                    platform=row[0],
                    content_count=row[1],
                    violations_count=row[2],
                    avg_similarity_score=float(row[3]) if row[3] else 0.0
                ))
            
            return platform_analytics
            
    except Exception as e:
        logger.error(f"Get platform analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform analytics"
        )