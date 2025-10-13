"""
AI Learning & Feedback Routes
API pour l'auto-amélioration IA via feedback utilisateurs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import sys
sys.path.append('/workspaces/iacherie/ia2good/microservices/guardian')

from services.ai_learning_service import get_learning_service
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/ai-learning", tags=["AI Learning"])
logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST MODELS
# ============================================================================

class FeedbackRequest(BaseModel):
    """Feedback utilisateur sur génération IA"""
    model_id: str = Field(..., description="ID du modèle utilisé")
    task_type: str = Field(..., description="Type de tâche: image, text, video, audio, etc.")
    score: float = Field(..., ge=1, le=5, description="Score 1-5 étoiles")
    comment: Optional[str] = Field(None, description="Commentaire optionnel")


class ModelSelectionRequest(BaseModel):
    """Demande de sélection adaptative de modèle"""
    task_type: str = Field(..., description="Type de tâche")
    quality_preference: Optional[str] = Field("balanced", description="Préférence qualité: fast, balanced, high")
    max_cost: Optional[float] = Field(None, description="Coût maximum par requête")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte additionnel")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    📊 Soumettre un feedback sur une génération IA
    
    Le système apprend automatiquement avec seulement 3 feedbacks (Few-Shot Learning)
    et adapte ses recommandations en continu.
    
    Returns:
        Analyse du feedback avec recommandations éventuelles
    """
    try:
        service = get_learning_service()
        
        result = await service.process_user_feedback(
            user_id=current_user.get("user_id", "anonymous"),
            model_id=request.model_id,
            task_type=request.task_type,
            score=request.score,
            comment=request.comment
        )
        
        return {
            "status": "success",
            "message": "Feedback enregistré et analysé",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Erreur feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-model")
async def adaptive_model_selection(
    request: ModelSelectionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    🤖 Sélection adaptative de modèle basée sur l'apprentissage
    
    Le système recommande le meilleur modèle basé sur:
    - Historique de feedbacks (Few-Shot Learning)
    - Préférences utilisateur
    - Performance des modèles
    - Coût et qualité
    
    Returns:
        Modèle recommandé avec raison et confiance
    """
    try:
        service = get_learning_service()
        
        recommendation = await service.adaptive_model_selection(
            task_type=request.task_type,
            user_id=current_user.get("user_id"),
            context=request.context
        )
        
        return {
            "status": "success",
            "recommendation": recommendation
        }
        
    except Exception as e:
        logger.error(f"Erreur sélection modèle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_learning_statistics(
    current_user: Dict = Depends(get_current_user)
):
    """
    📈 Statistiques d'apprentissage du système IA
    
    Affiche:
    - Nombre de feedbacks collectés
    - Modèles trackés et leurs performances
    - Top modèles par score
    - Cycles d'amélioration
    - Configuration Few-Shot Learning
    
    Returns:
        Statistiques complètes d'apprentissage
    """
    try:
        service = get_learning_service()
        stats = await service.get_learning_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def learning_service_health():
    """
    ❤️ Health check du service d'apprentissage
    
    Returns:
        Statut du service et configuration
    """
    try:
        service = get_learning_service()
        
        return {
            "status": "healthy",
            "service": "AI Learning Service",
            "features": {
                "few_shot_learning": True,
                "continuous_improvement": True,
                "adaptive_selection": True,
                "min_examples_required": 3
            },
            "last_improvement": service.last_improvement_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/best-models/{task_type}")
async def get_best_models_for_task(
    task_type: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    🏆 Meilleurs modèles pour un type de tâche
    
    Basé sur l'apprentissage et les feedbacks collectés
    
    Args:
        task_type: Type de tâche (image, text, video, audio, etc.)
        
    Returns:
        Liste des meilleurs modèles avec scores
    """
    try:
        service = get_learning_service()
        
        # Récupère le meilleur modèle appris
        best_model = service.metrics.get_best_model(task_type)
        
        if not best_model:
            return {
                "status": "no_data",
                "message": f"Aucune donnée d'apprentissage pour {task_type}",
                "recommendation": "Utilisez /select-model pour obtenir une recommandation"
            }
        
        avg_score = service.metrics.get_average_score(best_model)
        feedbacks_count = len(service.metrics.feedback_data[best_model])
        
        return {
            "status": "success",
            "task_type": task_type,
            "best_model": {
                "model_id": best_model,
                "average_score": avg_score,
                "feedbacks_count": feedbacks_count,
                "confidence": avg_score / 5.0
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur meilleurs modèles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
