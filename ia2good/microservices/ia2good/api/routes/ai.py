"""
Routes AI pour Guardian - Intégration avec IACherie
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List, Dict, Any
import sys
import os

# Add shared-services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

try:
    from ai_orchestrator import get_orchestrator
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

router = APIRouter(prefix="/ai", tags=["AI Integration"])


# =============================================
# AUDIO TRANSCRIPTION (Whisper)
# =============================================

@router.post("/transcribe-testimony")
async def transcribe_testimony(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("auto")
):
    """
    Transcrire témoignage audio humanitaire
    
    Utilise: Whisper Large (100+ langues)
    Priority: HIGH (IA2GOOD humanitaire gratuit)
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        # Read audio file
        audio_bytes = await audio_file.read()
        
        # Call IACherie Whisper model
        orchestrator = get_orchestrator()
        result = await orchestrator.guardian_transcribe_testimony(
            audio_file=audio_bytes,
            language=language
        )
        
        return {
            "success": True,
            "transcription": result.get("text", ""),
            "language_detected": result.get("language", language),
            "category": result.get("category", {}),
            "confidence": result.get("confidence", 0)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# =============================================
# TEXT GENERATION (Mission Descriptions)
# =============================================

@router.post("/generate-mission-description")
async def generate_mission_description(
    mission_type: str,
    location: str,
    duration: str,
    skills: List[str],
    context: str,
    language: str = "fr"
):
    """
    Générer description de mission humanitaire engageante
    
    Utilise: AI Leader GPT-XL
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        description = await orchestrator.guardian_generate_mission_description(
            mission_details={
                "type": mission_type,
                "location": location,
                "duration": duration,
                "skills": skills,
                "context": context
            },
            language=language
        )
        
        return {
            "success": True,
            "description": description,
            "language": language
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# =============================================
# VOLUNTEER MATCHING (AI Recommendations)
# =============================================

@router.post("/match-volunteers")
async def match_volunteers(
    mission: Dict[str, Any],
    volunteers_pool: List[Dict[str, Any]],
    max_results: int = 10
):
    """
    Matcher volontaires avec missions humanitaires
    
    Utilise: User Recommendation model
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        matches = await orchestrator.guardian_match_volunteers(
            mission=mission,
            volunteers_pool=volunteers_pool
        )
        
        # Limiter résultats
        matches = matches[:max_results]
        
        return {
            "success": True,
            "total_matches": len(matches),
            "matches": matches
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


# =============================================
# MULTILINGUAL TRANSLATION
# =============================================

@router.post("/translate-multilingual")
async def translate_multilingual(
    text: str,
    target_languages: List[str]
):
    """
    Traduire contenu en plusieurs langues (pour réfugiés, missions internationales)
    
    Utilise: Translation model (100+ langues)
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        translations = await orchestrator.guardian_translate_multilingual(
            text=text,
            target_languages=target_languages
        )
        
        return {
            "success": True,
            "original_text": text,
            "translations": translations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# =============================================
# IMAGE GENERATION (Campaign illustrations)
# =============================================

@router.post("/generate-campaign-image")
async def generate_campaign_image(
    prompt: str,
    style: str = "photorealistic",
    width: int = 1024,
    height: int = 1024
):
    """
    Générer image pour campagne humanitaire
    
    Utilise: SDXL Turbo
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        from iacherie_ai_client import get_ai_client, IAModelType
        
        client = get_ai_client()
        result = await client.generate_image(
            prompt=f"{prompt}, {style} style, humanitarian photography",
            model=IAModelType.SDXL_TURBO,
            width=width,
            height=height
        )
        
        return {
            "success": True,
            "image_url": result.get("image_url"),
            "prompt": prompt
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


# =============================================
# CONTENT CLASSIFICATION
# =============================================

@router.post("/classify-humanitarian-need")
async def classify_humanitarian_need(
    testimony: str,
    language: str = "auto"
):
    """
    Classifier type de besoin humanitaire à partir d'un témoignage
    
    Utilise: Content Classification model
    Priority: HIGH
    
    Catégories: natural_disaster, conflict, health_crisis, education_need, 
                food_insecurity, shelter, protection
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        from iacherie_ai_client import get_ai_client
        
        client = get_ai_client()
        result = await client.classify_content(
            content=testimony,
            categories=[
                "natural_disaster",
                "conflict",
                "health_crisis",
                "education_need",
                "food_insecurity",
                "shelter",
                "protection",
                "water_sanitation"
            ]
        )
        
        return {
            "success": True,
            "testimony": testimony,
            "category": result.get("category"),
            "confidence": result.get("confidence", 0),
            "all_scores": result.get("scores", {})
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


# =============================================
# HEALTH CHECK
# =============================================

@router.get("/health")
async def ai_health_check():
    """Vérifier que IACherie AI est disponible"""
    if not AI_ENABLED:
        return {
            "status": "disabled",
            "message": "AI integration not available"
        }
    
    try:
        orchestrator = get_orchestrator()
        health = await orchestrator.health_check()
        
        return {
            "status": "healthy",
            "iacherie_api": health
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
