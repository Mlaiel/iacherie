"""
Routes AI pour EduVerify - Intégration avec IACherie
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import sys
import os

# Add shared-services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

try:
    from ai_orchestrator import get_orchestrator
    from iacherie_ai_client import get_ai_client
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

router = APIRouter(prefix="/ai", tags=["AI Integration - EduVerify"])


# =============================================
# PYDANTIC MODELS
# =============================================

class ContentVerificationRequest(BaseModel):
    content: str
    sources: Optional[List[str]] = ["wikipedia", "scholarly", "duckduckgo"]


class QuizGenerationRequest(BaseModel):
    educational_content: str
    num_questions: int = 5
    difficulty: str = "medium"


class SummaryRequest(BaseModel):
    educational_content: str
    target_level: str = "high_school"  # elementary, middle_school, high_school, university


# =============================================
# FACT-CHECKING & VERIFICATION
# =============================================

@router.post("/fact-check")
async def fact_check_content(request: ContentVerificationRequest):
    """
    Vérifier contenu éducatif (fact-checking)
    
    Utilise: Content Classification + Fact Check models
    Priority: HIGH (IA2GOOD humanitaire gratuit)
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.eduverify_fact_check_content(
            educational_content=request.content,
            sources=request.sources
        )
        
        return {
            "success": True,
            "content": request.content,
            "verified": result.get("verified", False),
            "quality_score": result.get("quality_score", 0),
            "fact_check": result.get("fact_check", {}),
            "recommendations": result.get("recommendations", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact-checking failed: {str(e)}")


# =============================================
# TEXT GENERATION & SUMMARIZATION
# =============================================

@router.post("/generate-summary")
async def generate_summary(request: SummaryRequest):
    """
    Générer résumé de contenu éducatif adapté au niveau
    
    Utilise: AI Leader GPT-XL / Text Pro
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        summary = await orchestrator.eduverify_generate_summary(
            educational_content=request.educational_content,
            target_level=request.target_level
        )
        
        return {
            "success": True,
            "original_length": len(request.educational_content),
            "summary": summary,
            "summary_length": len(summary),
            "target_level": request.target_level
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


# =============================================
# QUIZ GENERATION
# =============================================

@router.post("/generate-quiz")
async def generate_quiz(request: QuizGenerationRequest):
    """
    Générer quiz QCM à partir de contenu éducatif - VRAIE IMPLÉMENTATION
    
    Utilise: AI Leader Internal Generator (GRATUIT)
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        # Call IACherie directly for structured quiz generation
        client = get_ai_client()
        
        # Use IACherie's dedicated quiz endpoint with real implementation
        response = await client.client.post("/api/ai-agents/generate-quiz", json={
            "content": request.educational_content,
            "num_questions": request.num_questions,
            "difficulty": request.difficulty
        })
        response.raise_for_status()
        quiz_data = response.json()
        
        return {
            "success": True,
            "message": "Quiz generated with real AI implementation",
            "quiz": quiz_data,
            "provider": "AI Leader (Internal)",
            "cost": 0.0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


# =============================================
# CONTENT QUALITY ASSESSMENT
# =============================================

@router.post("/assess-quality")
async def assess_content_quality(content: str):
    """
    Évaluer qualité du contenu éducatif
    
    Utilise: Quality Assessment model
    Priority: HIGH
    
    Retourne: score de qualité, lisibilité, structure, précision
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        client = get_ai_client()
        result = await client.assess_quality(
            content=content,
            content_type="educational"
        )
        
        return {
            "success": True,
            "quality_score": result.get("score", 0),
            "readability": result.get("readability", {}),
            "structure": result.get("structure", {}),
            "accuracy": result.get("accuracy", {}),
            "improvements": result.get("improvements", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality assessment failed: {str(e)}")


# =============================================
# SEO OPTIMIZATION
# =============================================

@router.post("/optimize-seo")
async def optimize_content_seo(
    content: str,
    target_keywords: List[str]
):
    """
    Optimiser contenu éducatif pour SEO
    
    Utilise: SEO Optimization model
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.eduverify_optimize_seo(
            educational_content=content,
            target_keywords=target_keywords
        )
        
        return {
            "success": True,
            "original_content": content,
            "optimized_content": result.get("optimized_content", ""),
            "keywords_used": result.get("keywords_used", []),
            "seo_score": result.get("seo_score", 0),
            "suggestions": result.get("suggestions", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEO optimization failed: {str(e)}")


# =============================================
# TEXT CORRECTION & IMPROVEMENT
# =============================================

@router.post("/correct-text")
async def correct_educational_text(
    text: str,
    language: str = "fr"
):
    """
    Corriger grammaire et orthographe
    
    Utilise: Text Pro
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        from iacherie_ai_client import IAModelType
        
        client = get_ai_client()
        result = await client.generate_text(
            prompt=f"Corrige la grammaire et l'orthographe de ce texte éducatif en {language}:\n\n{text}\n\nTexte corrigé:",
            model=IAModelType.TEXT_PRO,
            max_tokens=len(text) * 2,
            temperature=0.3  # Low temperature for accuracy
        )
        
        corrected_text = result.get("text", "")
        
        return {
            "success": True,
            "original_text": text,
            "corrected_text": corrected_text,
            "language": language,
            "changes_detected": corrected_text != text
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text correction failed: {str(e)}")


# =============================================
# CONTENT CLASSIFICATION
# =============================================

@router.post("/classify-subject")
async def classify_educational_subject(content: str):
    """
    Classifier matière éducative (Math, Science, Histoire, etc.)
    
    Utilise: Content Classification model
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        client = get_ai_client()
        result = await client.classify_content(
            content=content,
            categories=[
                "mathematics",
                "science",
                "history",
                "geography",
                "literature",
                "languages",
                "arts",
                "physical_education",
                "computer_science",
                "philosophy"
            ]
        )
        
        return {
            "success": True,
            "content": content,
            "subject": result.get("category"),
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
            "module": "eduverify",
            "iacherie_api": health
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
