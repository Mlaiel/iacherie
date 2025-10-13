"""
Routes IA pour EduVerify - Vérification de contenu éducatif
Utilise les modèles IACherie : Content Classification, Fact Check, GPT, SEO
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
import sys
import os

# Ajouter le chemin des shared services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

from ai_orchestrator import get_orchestrator
from iacherie_ai_client import get_ai_client

router = APIRouter(prefix="/ai", tags=["EduVerify AI"])


@router.post("/fact-check")
async def fact_check_content(
    content: str = Body(..., embed=True),
    sources: Optional[List[str]] = Body(None)
) -> Dict[str, Any]:
    """
    Vérifier contenu éducatif (fact-checking) - VRAIE IMPLÉMENTATION
    Utilise AI Leader Internal Fact-Checker (GRATUIT)
    """
    try:
        # Call IACherie directly for real fact-checking
        client = get_ai_client()
        
        response = await client.client.post("/api/ai-agents/fact-check", json={
            "claim": content,
            "sources": sources or ["knowledge_base", "scientific_consensus"],
            "domain": "education"
        })
        response.raise_for_status()
        fact_check_data = response.json()
        
        return {
            "success": True,
            "message": "Fact-check completed with REAL AI",
            "verified": fact_check_data.get("verified", False),
            "confidence": fact_check_data.get("confidence", 0.0),
            "verdict": fact_check_data.get("verdict", "Unknown"),
            "evidence": fact_check_data.get("evidence", []),
            "recommendations": fact_check_data.get("recommendations", []),
            "provider": "AI Leader (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur fact-checking: {str(e)}")


@router.post("/generate-summary")
async def generate_summary(
    content: str = Body(..., embed=True),
    target_level: str = Body("high_school", embed=True),
    style: str = Body("concise", embed=True)
) -> Dict[str, Any]:
    """
    Générer résumé de contenu éducatif - VRAIE IMPLÉMENTATION
    
    Niveaux disponibles:
    - elementary (primaire)
    - middle_school (collège)  
    - high_school (lycée)
    - university (université)
    
    Styles: concise, detailed, bullet_points
    """
    try:
        # Call IACherie directly for real summary generation
        client = get_ai_client()
        
        response = await client.client.post("/api/ai-agents/summarize", json={
            "content": content,
            "style": style,
            "max_length": 500
        })
        response.raise_for_status()
        summary_data = response.json()
        
        return {
            "success": True,
            "message": "Summary generated with REAL AI",
            "summary": summary_data.get("summary", ""),
            "target_level": target_level,
            "style": style,
            "original_length": summary_data.get("original_length", len(content)),
            "summary_length": summary_data.get("summary_length", 0),
            "compression_ratio": summary_data.get("compression_ratio", 0),
            "provider": "AI Leader (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération résumé: {str(e)}")


@router.post("/generate-quiz")
async def generate_quiz(
    content: str = Body(..., embed=True),
    num_questions: int = Body(5, embed=True)
) -> Dict[str, Any]:
    """
    Générer quiz QCM à partir de contenu éducatif - VRAIE IMPLÉMENTATION
    Utilise AI Leader Internal Generator (GRATUIT)
    """
    try:
        # Call IACherie directly for structured quiz generation with real AI
        client = get_ai_client()
        
        response = await client.client.post("/api/ai-agents/generate-quiz", json={
            "content": content,
            "num_questions": num_questions,
            "difficulty": "medium"
        })
        response.raise_for_status()
        quiz_data = response.json()
        
        return {
            "success": True,
            "message": "Quiz generated with REAL AI implementation",
            "quiz": quiz_data,
            "provider": "AI Leader (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération quiz: {str(e)}")


@router.post("/optimize-seo")
async def optimize_seo(
    content: str = Body(..., embed=True),
    keywords: List[str] = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Optimiser contenu éducatif pour SEO
    Utilise SEO Optimization model
    """
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.eduverify_optimize_seo(
            educational_content=content,
            target_keywords=keywords
        )
        
        return {
            "success": True,
            "optimized_content": result.get("optimized_content", ""),
            "seo_score": result.get("score", 0),
            "suggestions": result.get("suggestions", []),
            "keywords_used": keywords
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur optimisation SEO: {str(e)}")


@router.post("/assess-quality")
async def assess_quality(
    content: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Évaluer la qualité du contenu éducatif
    
    Critères:
    - Exactitude factuelle
    - Clarté de l'explication
    - Structure pédagogique
    - Niveau de langage
    - Présence d'exemples
    """
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.eduverify_fact_check_content(
            educational_content=content,
            sources=["wikipedia", "scholarly"]
        )
        
        quality_score = result["quality_score"]
        
        # Déterminer le niveau de qualité
        if quality_score >= 0.8:
            quality_level = "Excellent"
            color = "green"
        elif quality_score >= 0.6:
            quality_level = "Bon"
            color = "blue"
        elif quality_score >= 0.4:
            quality_level = "Acceptable"
            color = "orange"
        else:
            quality_level = "À améliorer"
            color = "red"
        
        return {
            "success": True,
            "quality_score": quality_score,
            "quality_level": quality_level,
            "color": color,
            "verified": result["verified"],
            "recommendations": result["recommendations"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur évaluation qualité: {str(e)}")


@router.post("/correct-grammar")
async def correct_grammar(
    content: str = Body(..., embed=True),
    language: str = Body("fr", embed=True)
) -> Dict[str, Any]:
    """
    Corriger grammaire et orthographe
    Utilise Text Pro model
    """
    try:
        orchestrator = get_orchestrator()
        
        prompt = f"""
        Corrige les erreurs de grammaire et d'orthographe dans ce texte éducatif en {language}:
        
        {content}
        
        Fournis:
        1. Le texte corrigé
        2. Liste des corrections apportées
        3. Explications pédagogiques des erreurs
        """
        
        result = await orchestrator.client.generate_text(
            prompt=prompt,
            model="text-pro",
            max_tokens=800
        )
        
        return {
            "success": True,
            "corrected_text": result.get("text", ""),
            "language": language,
            "original_length": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur correction: {str(e)}")


@router.get("/health-check")
async def health_check() -> Dict[str, Any]:
    """Vérifier connexion à IACherie AI"""
    try:
        orchestrator = get_orchestrator()
        health = await orchestrator.health_check()
        return {
            "eduverify_ai_status": "operational",
            "iacherie_connection": health["status"],
            "timestamp": health["timestamp"]
        }
    except Exception as e:
        return {
            "eduverify_ai_status": "degraded",
            "iacherie_connection": "unhealthy",
            "error": str(e)
        }


@router.post("/classify-subject")
async def classify_subject(
    content: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Classifier le contenu éducatif par matière/sujet
    
    Catégories:
    - Mathématiques, Sciences, Histoire, Géographie,
    - Langues, Littérature, Informatique, Arts, etc.
    """
    try:
        orchestrator = get_orchestrator()
        
        categories = [
            "Mathématiques", "Sciences", "Physique", "Chimie", "Biologie",
            "Histoire", "Géographie", "Économie", "Philosophie",
            "Langues", "Littérature", "Informatique", "Arts", "Musique",
            "Sport", "Technologie", "Autre"
        ]
        
        result = await orchestrator.client.classify_content(
            content=content,
            categories=categories
        )
        
        return {
            "success": True,
            "primary_subject": result.get("category", "Autre"),
            "confidence": result.get("confidence", 0),
            "all_scores": result.get("scores", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur classification: {str(e)}")
