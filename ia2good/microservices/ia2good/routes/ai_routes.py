"""
Routes IA pour Guardian/Volunteer - Matching humanitaire
Utilise les modèles IACherie : Whisper, GPT, Translation, Recommendation
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from typing import Optional, List, Dict, Any
import sys
import os

# Ajouter le chemin des shared services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

from ai_orchestrator import get_orchestrator

router = APIRouter(prefix="/ai", tags=["Guardian AI"])


@router.post("/transcribe-testimony")
async def transcribe_testimony(
    audio_file: UploadFile = File(...),
    language: str = "auto"
) -> Dict[str, Any]:
    """
    Transcrire témoignage humanitaire (audio → texte)
    Supporte 100+ langues via Whisper Large
    """
    try:
        # Lire le fichier audio
        audio_bytes = await audio_file.read()
        
        orchestrator = get_orchestrator()
        result = await orchestrator.guardian_transcribe_testimony(
            audio_file=audio_bytes,
            language=language
        )
        
        return {
            "success": True,
            "text": result.get("text", ""),
            "language": result.get("language", language),
            "category": result.get("category", {}),
            "duration": result.get("duration", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur transcription: {str(e)}")


@router.post("/generate-mission-description")
async def generate_mission_description(
    mission_details: Dict[str, Any] = Body(...),
    language: str = Body("fr", embed=True)
) -> Dict[str, Any]:
    """
    Générer description engageante pour mission humanitaire
    
    Required fields in mission_details:
    - type: str (ex: "disaster_relief", "education", "health")
    - location: str
    - duration: str
    - skills: List[str]
    - context: str
    """
    try:
        orchestrator = get_orchestrator()
        description = await orchestrator.guardian_generate_mission_description(
            mission_details=mission_details,
            language=language
        )
        
        return {
            "success": True,
            "description": description,
            "language": language,
            "mission_type": mission_details.get("type", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération description: {str(e)}")


@router.post("/match-volunteers")
async def match_volunteers(
    mission: Dict[str, Any] = Body(...),
    volunteers: List[Dict[str, Any]] = Body(...)
) -> Dict[str, Any]:
    """
    Matcher volontaires avec missions humanitaires
    Utilise User Recommendation model
    
    Mission fields:
    - skills_required: List[str]
    - location: Dict (lat, lon)
    - duration: str
    - urgency: str
    
    Volunteer fields:
    - skills: List[str]
    - experience: List[str]
    - location: Dict
    - availability: str
    """
    try:
        orchestrator = get_orchestrator()
        matches = await orchestrator.guardian_match_volunteers(
            mission=mission,
            volunteers_pool=volunteers
        )
        
        # Trier par score de matching
        sorted_matches = sorted(
            matches,
            key=lambda x: x.get("match_score", 0),
            reverse=True
        )
        
        return {
            "success": True,
            "matches": sorted_matches,
            "total_candidates": len(volunteers),
            "qualified_candidates": len([m for m in matches if m.get("match_score", 0) >= 0.6])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur matching: {str(e)}")


@router.post("/translate-multilingual")
async def translate_multilingual(
    text: str = Body(..., embed=True),
    target_languages: List[str] = Body(...)
) -> Dict[str, Any]:
    """
    Traduire contenu en plusieurs langues
    Utile pour communications internationales (réfugiés, diaspora)
    
    Langues supportées: fr, en, ar, es, pt, de, it, ru, zh, ja, ko, hi, bn, pa, te, etc.
    """
    try:
        orchestrator = get_orchestrator()
        translations = await orchestrator.guardian_translate_multilingual(
            text=text,
            target_languages=target_languages
        )
        
        return {
            "success": True,
            "original_text": text,
            "translations": translations,
            "languages_count": len(target_languages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traduction: {str(e)}")


@router.post("/classify-need")
async def classify_humanitarian_need(
    description: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Classifier besoin humanitaire
    
    Catégories:
    - natural_disaster (désastres naturels)
    - conflict (conflits)
    - health_crisis (crises sanitaires)
    - education_need (besoins éducatifs)
    - food_insecurity (insécurité alimentaire)
    - shelter (hébergement)
    - protection (protection)
    """
    try:
        orchestrator = get_orchestrator()
        
        categories = [
            "natural_disaster", "conflict", "health_crisis",
            "education_need", "food_insecurity", "shelter",
            "protection", "displacement", "other"
        ]
        
        result = await orchestrator.client.classify_content(
            content=description,
            categories=categories
        )
        
        category = result.get("category", "other")
        confidence = result.get("confidence", 0)
        
        # Déterminer l'urgence basée sur la catégorie
        high_urgency_categories = ["natural_disaster", "conflict", "health_crisis"]
        urgency = "high" if category in high_urgency_categories else "moderate"
        
        return {
            "success": True,
            "category": category,
            "confidence": confidence,
            "urgency": urgency,
            "description_length": len(description)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur classification: {str(e)}")


@router.post("/generate-appeal")
async def generate_fundraising_appeal(
    mission: Dict[str, Any] = Body(...),
    target_audience: str = Body("general", embed=True),
    language: str = Body("fr", embed=True)
) -> Dict[str, Any]:
    """
    Générer appel de fonds pour mission humanitaire
    Utilise AI Leader GPT-XL
    
    Target audiences:
    - general (grand public)
    - corporate (entreprises)
    - foundations (fondations)
    - individual_donors (donateurs individuels)
    """
    try:
        orchestrator = get_orchestrator()
        
        prompt = f"""
        Génère un appel de fonds convaincant en {language} pour cette mission humanitaire:
        
        Type: {mission.get('type')}
        Localisation: {mission.get('location')}
        Contexte: {mission.get('context')}
        Objectif de financement: {mission.get('funding_goal', 'Non spécifié')}
        Audience cible: {target_audience}
        
        L'appel doit:
        - Être émotionnel mais factuel
        - Expliquer l'impact concret des dons
        - Inclure un appel à l'action clair
        - Respecter la dignité des bénéficiaires
        - Être adapté à l'audience {target_audience}
        """
        
        result = await orchestrator.client.generate_text(
            prompt=prompt,
            model="ai-leader-gpt-xl",
            max_tokens=500
        )
        
        return {
            "success": True,
            "appeal": result.get("text", ""),
            "language": language,
            "target_audience": target_audience
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération appel: {str(e)}")


@router.post("/analyze-sentiment")
async def analyze_testimony_sentiment(
    testimony: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Analyser le sentiment d'un témoignage
    Utile pour détecter détresse, urgence, traumatisme
    """
    try:
        orchestrator = get_orchestrator()
        
        prompt = f"""
        Analyse le sentiment et l'urgence de ce témoignage humanitaire:
        
        {testimony}
        
        Fournis:
        1. Sentiment général (positif, neutre, négatif, détresse)
        2. Niveau d'urgence (faible, moyen, élevé, critique)
        3. Besoins immédiats détectés
        4. Recommandations d'action
        """
        
        result = await orchestrator.client.generate_text(
            prompt=prompt,
            model="ai-leader-gpt-xl",
            max_tokens=400
        )
        
        return {
            "success": True,
            "analysis": result.get("text", ""),
            "testimony_length": len(testimony)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse sentiment: {str(e)}")


@router.get("/health-check")
async def health_check() -> Dict[str, Any]:
    """Vérifier connexion à IACherie AI"""
    try:
        orchestrator = get_orchestrator()
        health = await orchestrator.health_check()
        return {
            "guardian_ai_status": "operational",
            "iacherie_connection": health["status"],
            "timestamp": health["timestamp"]
        }
    except Exception as e:
        return {
            "guardian_ai_status": "degraded",
            "iacherie_connection": "unhealthy",
            "error": str(e)
        }


@router.post("/generate-report")
async def generate_mission_report(
    mission_data: Dict[str, Any] = Body(...),
    report_type: str = Body("summary", embed=True),
    language: str = Body("fr", embed=True)
) -> Dict[str, Any]:
    """
    Générer rapport de mission
    
    Types de rapports:
    - summary (résumé exécutif)
    - detailed (rapport détaillé)
    - donor (rapport pour donateurs)
    - impact (rapport d'impact)
    """
    try:
        orchestrator = get_orchestrator()
        
        prompt = f"""
        Génère un rapport {report_type} en {language} pour cette mission humanitaire:
        
        Nom: {mission_data.get('name')}
        Durée: {mission_data.get('duration')}
        Localisation: {mission_data.get('location')}
        Bénéficiaires: {mission_data.get('beneficiaries', 0)}
        Budget: {mission_data.get('budget', 'Non spécifié')}
        Activités: {', '.join(mission_data.get('activities', []))}
        Résultats: {mission_data.get('results', 'En cours')}
        
        Le rapport doit inclure:
        - Contexte et objectifs
        - Activités réalisées
        - Résultats et impact
        - Défis rencontrés
        - Perspectives
        """
        
        result = await orchestrator.client.generate_text(
            prompt=prompt,
            model="ai-leader-gpt-xl",
            max_tokens=800
        )
        
        return {
            "success": True,
            "report": result.get("text", ""),
            "report_type": report_type,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")
