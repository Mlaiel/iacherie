"""
🎨 EXEMPLE D'INTÉGRATION AI LEADER AGENT

Démontre comment intégrer l'AI Leader Agent dans vos APIs existantes
pour observer et remplacer progressivement les APIs externes

Author: Fahed Mlaiel
Date: October 2025
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import logging
from typing import Optional

from backend.ai_leader_agent import (
    ai_leader_agent,
    observe_api_call_wrapper,
    execute_with_ai_fallback,
    APIType
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== MODÈLES ====================

class TextGenerationRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7


class ImageGenerationRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1024x1024"
    quality: Optional[str] = "standard"


class VideoGenerationRequest(BaseModel):
    prompt: str
    duration: Optional[int] = 10
    quality: Optional[str] = "hd"


# ==================== EXEMPLE 1: TEXT GENERATION ====================

@router.post("/example/text-generation")
async def text_generation_with_ai_leader(request: TextGenerationRequest):
    """
    Génération de texte avec AI Leader Agent
    
    Observe l'appel OpenAI et peut le remplacer automatiquement si l'API échoue
    """
    
    # Définir la fonction d'appel API externe
    async def call_openai_api(input_data):
        """
        Simule un appel à OpenAI GPT-4"""
        prompt = input_data["prompt"]
        
        # Simuler un appel API (dans la vraie vie, utiliser openai.chat.completions.create)
        import random
        
        # Simuler échec parfois pour tester le fallback
        if random.random() < 0.2:  # 20% de chance d'échec
            raise Exception("API OpenAI temporairement indisponible")
        
        # Simuler réponse
        return {
            "text": f"[OpenAI GPT-4] Réponse générée pour: {prompt[:50]}...",
            "model": "gpt-4",
            "tokens": 150
        }
    
    try:
        # Exécuter avec AI Leader Agent (fallback automatique si échec)
        result, provider = await execute_with_ai_fallback(
            api_name="OpenAI GPT-4",
            api_type="TEXT_GENERATION",
            input_data={
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            },
            external_api_func=call_openai_api
        )

        
        return {
            "success": True,
            "provider": provider,  # 'external' ou 'internal'
            "result": result,
            "message": f"Texte généré via {provider}"
        }
        
    except Exception as e:
        logger.error(f"Erreur génération texte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXEMPLE 2: IMAGE GENERATION ====================

@router.post("/example/image-generation")
async def image_generation_with_ai_leader(request: ImageGenerationRequest):
    """
    Génération d'images avec AI Leader Agent
    
    Observe DALL-E et peut basculer vers capacité interne
    """
    
    async def call_dalle_api(input_data):
        """
        Simule un appel à DALL-E"""
        prompt = input_data["prompt"]
        
        import random
        if random.random() < 0.2:
            raise Exception("API DALL-E rate limit exceeded")

        
        return {
            "image_url": f"https://example.com/dalle_image_{hash(prompt)}.png",
            "model": "dall-e-3",
            "size": input_data.get("size", "1024x1024")
        }
    
    try:
        result, provider = await execute_with_ai_fallback(
            api_name="DALL-E 3",
            api_type="IMAGE_GENERATION",
            input_data={
                "prompt": request.prompt,
                "size": request.size,
                "quality": request.quality
            },
            external_api_func=call_dalle_api
        )

        
        return {
            "success": True,
            "provider": provider,
            "result": result,
            "message": f"Image générée via {provider}"
        }
        
    except Exception as e:
        logger.error(f"Erreur génération image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXEMPLE 3: VIDEO GENERATION ====================

@router.post("/example/video-generation")
async def video_generation_with_ai_leader(request: VideoGenerationRequest):
    """
    Génération de vidéos avec AI Leader Agent
    
    Observe RunwayML et peut basculer vers capacité interne
    """
    
    async def call_runwayml_api(input_data):
        """
        Simule un appel à RunwayML Gen-3"""
        prompt = input_data["prompt"]
        
        import random
        if random.random() < 0.2:
            raise Exception("API RunwayML credits exhausted")

        
        return {
            "video_url": f"https://example.com/runwayml_video_{hash(prompt)}.mp4",
            "model": "gen-3-alpha",
            "duration": input_data.get("duration", 10)
        }
    
    try:
        result, provider = await execute_with_ai_fallback(
            api_name="RunwayML Gen-3",
            api_type="VIDEO_GENERATION",
            input_data={
                "prompt": request.prompt,
                "duration": request.duration,
                "quality": request.quality
            },
            external_api_func=call_runwayml_api
        )

        
        return {
            "success": True,
            "provider": provider,
            "result": result,
            "message": f"Vidéo générée via {provider}"
        }
        
    except Exception as e:
        logger.error(f"Erreur génération vidéo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXEMPLE 4: OBSERVATION MANUELLE ====================

@router.post("/example/manual-observation")
async def manual_api_observation():
    """
    Exemple d'observation manuelle d'un appel API
    
    Utilisez ceci si vous voulez observer sans le fallback automatique
    """
    
    start_time = time.time()
    
    try:
        # Votre appel API normal

        prompt = "Test prompt"
        response = f"Response for {prompt}"
        
        latency = time.time() - start_time
        
        # Observer l'appel pour l'agent
        await observe_api_call_wrapper(
            api_name="Custom API",
            api_type="TEXT_GENERATION",
            input_data={"prompt": prompt},
            output_data={"text": response},
            latency=latency,
            success=True,
            quality_score=0.85,
            cost=0.01
        )

        
        return {
            "success": True,
            "message": "Appel observé par l'AI Leader Agent",
            "latency": latency
        }
        
    except Exception as e:
        # Observer l'échec aussi
        await observe_api_call_wrapper(
            api_name="Custom API",
            api_type="TEXT_GENERATION",
            input_data={"prompt": "Test"},
            output_data={"error": str(e)},
            latency=time.time() - start_time,
            success=False,
            quality_score=0.0,
            cost=0.0
        )

        
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATISTIQUES D'UTILISATION ====================

@router.get("/example/usage-stats")
async def get_usage_stats():
    """
    Statistiques d'utilisation de l'AI Leader Agent
    """
    
    from backend.ai_leader_agent import get_ai_leader_status

    
    status = get_ai_leader_status()
    
    # Calculer économies
    total_calls = status["total_api_calls_observed"]
    replaced_calls = status["total_api_calls_replaced"]
    
    if total_calls > 0:
        replacement_rate = replaced_calls / total_calls
        
        # Estimation économies (en supposant $0.02 par appel externe vs $0.002 interne)

        external_cost = total_calls * 0.02

        internal_cost = replaced_calls * 0.002

        external_remaining_cost = (total_calls - replaced_calls) * 0.02

        total_current_cost = internal_cost + external_remaining_cost

        savings = external_cost - total_current_cost

        savings_percentage = (savings / external_cost * 100) if external_cost > 0 else 0
    else:
        replacement_rate = 0

        external_cost = 0

        savings = 0

        savings_percentage = 0
    
    return {
        "success": True,
        "usage": {
            "total_calls": total_calls,
            "external_calls": total_calls - replaced_calls,
            "internal_calls": replaced_calls,
            "replacement_rate": replacement_rate,
        },
        "costs": {
            "if_all_external": external_cost,
            "current_cost": total_current_cost if total_calls > 0 else 0,
            "savings": savings,
            "savings_percentage": savings_percentage
        },
        "agent": {
            "phase": status["phase"],
            "autonomy": status["autonomy_percentage"],
            "capabilities_ready": status["capabilities_ready"],
            "is_autonomous": status["is_fully_autonomous"]
        }
    }


# ==================== TEST AUTOMATIQUE ====================

@router.post("/example/run-test")
async def run_automated_test():
    """
    Lance un test automatique pour simuler des appels et voir l'agent apprendre
    """
    
    logger.info("🧪 Lancement du test automatique...")

    
    results = {
        "text_generation": [],
        "image_generation": [],
        "video_generation": []
    }
    
    # Test 10 appels de chaque type
    for i in range(10):
        # Text generation
        try:
            response = await text_generation_with_ai_leader(
                TextGenerationRequest(prompt=f"Test prompt {i}")
            )

            results["text_generation"].append({
                "success": True,
                "provider": response["provider"]
            })
        except Exception as e:
            results["text_generation"].append({
                "success": False,
                "error": str(e)
            })
        
        # Image generation
        try:
            response = await image_generation_with_ai_leader(
                ImageGenerationRequest(prompt=f"Test image {i}")
            )

            results["image_generation"].append({
                "success": True,
                "provider": response["provider"]
            })
        except Exception as e:
            results["image_generation"].append({
                "success": False,
                "error": str(e)
            })
        
        # Video generation
        try:
            response = await video_generation_with_ai_leader(
                VideoGenerationRequest(prompt=f"Test video {i}")
            )

            results["video_generation"].append({
                "success": True,
                "provider": response["provider"]
            })
        except Exception as e:
            results["video_generation"].append({
                "success": False,
                "error": str(e)
            })
    
    # Calculer statistiques
    text_success = sum(1 for r in results["text_generation"] if r["success"])
    text_internal = sum(1 for r in results["text_generation"] if r.get("provider") == "internal")

    
    image_success = sum(1 for r in results["image_generation"] if r["success"])
    image_internal = sum(1 for r in results["image_generation"] if r.get("provider") == "internal")

    
    video_success = sum(1 for r in results["video_generation"] if r["success"])
    video_internal = sum(1 for r in results["video_generation"] if r.get("provider") == "internal")
    
    return {
        "success": True,
        "message": "Test automatique complété",
        "summary": {
            "text_generation": {
                "total": 10,
                "success": text_success,
                "internal_provider": text_internal,
                "success_rate": text_success / 10
            },
            "image_generation": {
                "total": 10,
                "success": image_success,
                "internal_provider": image_internal,
                "success_rate": image_success / 10
            },
            "video_generation": {
                "total": 10,
                "success": video_success,
                "internal_provider": video_internal,
                "success_rate": video_success / 10
            }
        },
        "detailed_results": results
    }
