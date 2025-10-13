"""
🎯 ENDPOINT BACKEND MIDJOURNEY DISCORD
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.integrations.midjourney_discord_bot import generate_midjourney_discord
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/midjourney", tags=["midjourney"])


class MidjourneyRequest(BaseModel):
    prompt: str
    wait: bool = True


@router.post("/generate")
async def generate_image(request: MidjourneyRequest):
    """
    Génère une image via Midjourney Discord Bot
    """
    try:
        logger.info(f"Génération Midjourney: {request.prompt[:50]}...")


        
        result = await generate_midjourney_discord(request.prompt)

        
        if not result or not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Erreur génération Midjourney')
            )

        
        return {
            "success": True,
            "image_url": result.get('image_url'),
            "message_id": result.get('message_id'),
            "duration": result.get('duration', 0)
        }
        
    except Exception as e:
        logger.error(f"Erreur Midjourney: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
