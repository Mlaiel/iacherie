"""
🕷️ CRAWLERS API ENDPOINTS
===========================
API pour contrôler les 13+ crawlers
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from backend.core.crawlers_gateway import crawlers_gateway

router = APIRouter()
logger = logging.getLogger(__name__)

class CrawlRequest(BaseModel):
    """
        Requête de crawl"""
    target: str
    options: Dict[str, Any] = {}

class CrawlerStatus(BaseModel):
    """
        Status d'un crawler"""
    crawler_name: str
    status: str
    last_run: Optional[str] = None

@router.get("/crawlers")
async def list_crawlers():
    """📋 Liste tous les crawlers disponibles"""
    try:
        crawlers_info = crawlers_gateway.list_crawlers()
        return {
            "success": True,
            "total_crawlers": crawlers_info["total"],
            "crawlers": crawlers_info["crawlers"],
            "supported_platforms": [
                "YouTube", "Instagram", "TikTok", "Twitter", "Facebook",
                "LinkedIn", "Pinterest", "Snapchat", "Discord", "Reddit", "Telegram"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error listing crawlers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawlers/{crawler_name}/crawl")
async def crawl_target(crawler_name: str, request: CrawlRequest):
    """🕷️ Lance un crawler sur une cible"""
    try:
        result = await crawlers_gateway.crawl(
            crawler_name=crawler_name,
            target=request.target,
            **request.options
        )

        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "non trouvé" in result.get("error", "") else 500,
                detail=result.get("error", "Unknown error")
            )

        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Crawl error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawlers/{crawler_name}/status")
async def get_crawler_status(crawler_name: str):
    """📊 Status d'un crawler spécifique"""
    try:
        crawlers_info = crawlers_gateway.list_crawlers()

        
        if crawler_name not in crawlers_info["crawlers"]:
            raise HTTPException(status_code=404, detail=f"Crawler {crawler_name} not found")

        
        return {
            "success": True,
            "crawler_name": crawler_name,
            "type": crawlers_info["crawlers"][crawler_name],
            "status": "ready",
            "available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawlers/platforms/supported")
async def get_supported_platforms():
    """🌐 Liste toutes les plateformes supportées"""
    return {
        "success": True,
        "total_platforms": 11,
        "platforms": [
            {
                "name": "YouTube",
                "crawler": "youtube",
                "features": ["Video tracking", "Channel monitoring", "Comment analysis"]
            },
            {
                "name": "Instagram", 
                "crawler": "instagram",
                "features": ["Post tracking", "Story monitoring", "Profile analysis"]
            },
            {
                "name": "TikTok",
                "crawler": "tiktok", 
                "features": ["Video tracking", "Trend monitoring", "Sound analysis"]
            },
            {
                "name": "Twitter/X",
                "crawler": "twitter",
                "features": ["Tweet tracking", "Trend monitoring", "Engagement analysis"]
            },
            {
                "name": "Facebook",
                "crawler": "social_media_platforms",
                "features": ["Post tracking", "Page monitoring", "Engagement analysis"]
            },
            {
                "name": "LinkedIn",
                "crawler": "professional_networks",
                "features": ["Post tracking", "Profile monitoring", "Network analysis"]
            },
            {
                "name": "Pinterest",
                "crawler": "social_media_platforms",
                "features": ["Pin tracking", "Board monitoring", "Trend analysis"]
            },
            {
                "name": "Snapchat",
                "crawler": "social_media_platforms",
                "features": ["Story tracking", "Spotlight monitoring"]
            },
            {
                "name": "Discord",
                "crawler": "social_media_platforms",
                "features": ["Server monitoring", "Channel tracking", "Message analysis"]
            },
            {
                "name": "Reddit",
                "crawler": "social_media_platforms",
                "features": ["Post tracking", "Subreddit monitoring", "Comment analysis"]
            },
            {
                "name": "Telegram",
                "crawler": "social_media_platforms",
                "features": ["Channel monitoring", "Group tracking", "Message analysis"]
            }
        ]
    }
