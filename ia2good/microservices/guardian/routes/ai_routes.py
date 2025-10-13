"""
Guardian AI Endpoints
Assistance IA pour missions humanitaires, environnement, animaux, sans-abri
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os

router = APIRouter()

# AI Assistance request model
class AIRequest(BaseModel):
    query: str
    context: Optional[str] = None
    category: Optional[str] = None  # environment, animal, homeless, humanitarian

class AIResponse(BaseModel):
    result: str
    source: str
    model: str

IACHERIE_API_URL = os.getenv("IACHERIE_API_URL", "http://localhost:8000")
IACHERIE_API_KEY = os.getenv("IACHERIE_API_KEY")

@router.post("/ai", response_model=AIResponse)
def ai_assist(request: AIRequest):
    """Obtenir une assistance IA pour une mission"""
    payload = {
        "prompt": request.query,
        "context": request.context,
        "category": request.category or "humanitarian",
        "model": "internal-guardian-volunteer"
    }
    headers = {"Authorization": f"Bearer {IACHERIE_API_KEY}"} if IACHERIE_API_KEY else {}
    try:
        response = requests.post(f"{IACHERIE_API_URL}/api/generate/text", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        result_text = data.get("result", data.get("text", "No result"))
        return AIResponse(result=result_text, source="IACherie", model="internal-guardian-volunteer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI assistance failed: {e}")
