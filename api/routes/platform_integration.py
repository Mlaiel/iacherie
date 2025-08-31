"""Platform Integration API Routes
Integration with social media and content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.logging import logger


# Pydantic models
class PlatformConnection(BaseModel):
    platform: str
    connected: bool
    username: Optional[str] = None
    connected_at: Optional[str] = None


class ContentDistribution(BaseModel):
    content_id: str
    platform: str
    platform_url: Optional[str] = None
    status: str
    distributed_at: str


# Router setup
router = APIRouter()


@router.get("/connections", response_model=List[PlatformConnection])
async def get_platform_connections(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get user's platform connections"""    try:
        user_id = current_user["user_id"]
        
        # Supported platforms
        supported_platforms = ["youtube", "instagram", "tiktok", "twitter", "spotify"]
        
        connections = []
        
        async with database_manager.get_postgres_session() as session:
            for platform in supported_platforms:
                result = await session.execute(
                    """                    SELECT platform_username, connected_at 
                    FROM platform_connections 
                    WHERE user_id = %s AND platform = %s AND active = true
                    """,
                    (user_id, platform)
                )
                
                row = result.fetchone()
                
                connections.append(PlatformConnection(
                    platform=platform,
                    connected=row is not None,
                    username=row[0] if row else None,
                    connected_at=row[1].isoformat() if row else None
                ))
        
        return connections
        
    except Exception as e:
        logger.error(f"Get platform connections failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform connections"
        )


@router.get("/recommendations")
async def get_platform_recommendations(
    content_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get platform recommendations for content"""    try:
        user_id = current_user["user_id"]
        
        if content_id:
            # Get specific content recommendations
            analysis_collection = await database_manager.get_mongodb_collection("content_analysis")
            analysis_doc = await analysis_collection.find_one({
                "content_id": content_id,
                "user_id": user_id
            }, sort=[("created_at", -1)])
            
            if analysis_doc:
                analysis_result = analysis_doc.get("analysis_result", {})
                recommendations = analysis_result.get("platform_recommendations", [])
                return {"recommendations": recommendations}
        
        # General platform recommendations
        return {
            "recommendations": [
                {
                    "platform": "youtube",
                    "suitability_score": 85.0,
                    "reasons": ["Great for video content", "High monetization potential"],
                    "optimization_tips": ["Create compelling thumbnails", "Optimize title with keywords"]
                },
                {
                    "platform": "instagram",
                    "suitability_score": 78.0,
                    "reasons": ["Visual content performs well", "High engagement rates"],
                    "optimization_tips": ["Use 11 relevant hashtags", "Post during peak hours"]
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Get platform recommendations failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform recommendations"
        )