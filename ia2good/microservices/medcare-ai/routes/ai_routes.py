"""
Routes IA pour MedCare - Assistance médicale avec IA
Utilise les modèles IACherie : Whisper, GPT, TTS, Translation
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from typing import Optional, List, Dict, Any
import sys
import os

# Ajouter le chemin des shared services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

from ai_orchestrator import get_orchestrator
from iacherie_ai_client import get_ai_client

router = APIRouter(prefix="/ai", tags=["MedCare AI"])


@router.post("/analyze-symptoms")
async def analyze_symptoms(
    symptoms: str = Body(..., embed=True),
    language: str = Body("fr", embed=True),
    severity: int = Body(5, embed=True)
) -> Dict[str, Any]:
    """
    Analyser symptômes avec IA médicale - VRAIE IMPLÉMENTATION
    
    ⚠️ IMPORTANT: Ceci est une assistance IA, pas un diagnostic médical.
    Toujours consulter un médecin professionnel.
    """
    try:
        # Parse symptoms into list
        symptoms_list = [s.strip() for s in symptoms.split(",")]
        
        # Call IACherie directly for real medical analysis
        client = get_ai_client()
        
        response = await client.client.post("/api/ai-agents/medical/symptom-analysis", json={
            "symptoms": symptoms_list,
            "severity": severity
        })
        response.raise_for_status()
        analysis_data = response.json()
        
        return {
            "success": True,
            "message": "Medical analysis completed with REAL AI",
            "analysis": analysis_data.get("medical_analysis", ""),
            "urgency": analysis_data.get("urgency", "routine"),
            "severity": analysis_data.get("severity", severity),
            "categories": analysis_data.get("categories", {}),
            "recommendations": analysis_data.get("recommendations", []),
            "red_flags": analysis_data.get("red_flags", []),
            "language": language,
            "disclaimer": "⚠️ Ceci n'est PAS un diagnostic médical. Consultez toujours un médecin qualifié.",
            "provider": "AI Leader Medical (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse symptômes: {str(e)}")


@router.post("/transcribe-consultation")
async def transcribe_consultation(
    audio_file: UploadFile = File(...),
    language: str = "fr"
) -> Dict[str, Any]:
    """
    Transcrire consultation médicale (audio → texte)
    Utilise Whisper Large pour transcription multilingue
    """
    try:
        # Lire le fichier audio
        audio_bytes = await audio_file.read()
        
        orchestrator = get_orchestrator()
        result = await orchestrator.medcare_transcribe_consultation(
            audio_file=audio_bytes,
            language=language
        )
        
        return {
            "success": True,
            "transcription": result.get("text", ""),
            "language": result.get("language", language),
            "medical_analysis": result.get("medical_analysis", {}),
            "duration": result.get("duration", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur transcription: {str(e)}")


@router.post("/generate-voice-advice")
async def generate_voice_advice(
    medical_advice: str = Body(..., embed=True),
    language: str = Body("fr", embed=True),
    voice: str = Body("medical_professional", embed=True)
) -> Dict[str, Any]:
    """
    Générer recommandations médicales en audio (TTS)
    Utilise TTS Pro pour synthèse vocale
    """
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.medcare_generate_voice_advice(
            medical_advice=medical_advice,
            language=language,
            voice=voice
        )
        return {
            "success": True,
            "audio_url": result.get("audio_url", ""),
            "duration": result.get("duration", 0),
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération audio: {str(e)}")


@router.post("/translate-medical-terms")
async def translate_medical_terms(
    terms: List[str] = Body(...),
    source_language: str = Body("fr", embed=True),
    target_language: str = Body("en", embed=True)
) -> Dict[str, Any]:
    """
    Traduire terminologie médicale - VRAIE IMPLÉMENTATION
    Utile pour patients non-francophones
    """
    try:
        # Call IACherie translation endpoint
        client = get_ai_client()
        
        translations = {}
        for term in terms:
            response = await client.client.post("/api/languages/translate", json={
                "text": term,
                "source_language": source_language,
                "target_language": target_language,
                "domain": "medical"
            })
            response.raise_for_status()
            translation_data = response.json()
            translations[term] = translation_data.get("translated_text", term)
        
        return {
            "success": True,
            "message": "Medical terms translated with REAL AI",
            "translations": translations,
            "source_language": source_language,
            "target_language": target_language,
            "count": len(translations),
            "provider": "AI Leader Translation (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traduction: {str(e)}")


@router.post("/recommend-specialists")
async def recommend_specialists(
    symptoms: str = Body(...),
    location: Dict[str, float] = Body(...),
    user_profile: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Recommander spécialistes médicaux basé sur symptômes et localisation
    Utilise User Recommendation model
    """
    try:
        orchestrator = get_orchestrator()
        recommendations = await orchestrator.medcare_recommend_specialists(
            symptoms=symptoms,
            location=location,
            user_profile=user_profile
        )
        return {
            "success": True,
            "specialists": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recommandation: {str(e)}")


@router.get("/health-check")
async def health_check() -> Dict[str, Any]:
    """Vérifier connexion à IACherie AI"""
    try:
        orchestrator = get_orchestrator()
        health = await orchestrator.health_check()
        return {
            "medcare_ai_status": "operational",
            "iacherie_connection": health["status"],
            "timestamp": health["timestamp"]
        }
    except Exception as e:
        return {
            "medcare_ai_status": "degraded",
            "iacherie_connection": "unhealthy",
            "error": str(e)
        }


@router.post("/emergency-triage")
async def emergency_triage(
    symptoms: str = Body(..., embed=True),
    vital_signs: Optional[Dict[str, float]] = Body(None)
) -> Dict[str, Any]:
    """
    Triage d'urgence - Déterminer la priorité médicale - VRAIE IMPLÉMENTATION
    
    Catégories:
    - EMERGENCY: Appeler 911 immédiatement
    - URGENT: Consulter dans les 2-4 heures
    - MODERATE: Consulter dans 24-48 heures
    - MINOR: Surveillance, consultation non-urgente
    """
    try:
        # Parse symptoms
        symptoms_list = [s.strip() for s in symptoms.split(",")]
        
        # Determine severity from vital signs
        severity = 5  # default
        if vital_signs:
            # High fever or abnormal vitals = higher severity
            if vital_signs.get("temperature", 37) > 39:
                severity = 8
            if vital_signs.get("heart_rate", 70) > 120:
                severity = 7
            if vital_signs.get("blood_pressure_systolic", 120) > 180:
                severity = 9
        
        # Call IACherie for real medical analysis
        client = get_ai_client()
        
        response = await client.client.post("/api/ai-agents/medical/symptom-analysis", json={
            "symptoms": symptoms_list,
            "severity": severity
        })
        response.raise_for_status()
        analysis_data = response.json()
        
        urgency = analysis_data.get("urgency", "routine")
        
        # Déterminer actions
        actions = {
            "emergency": [
                "🚨 Appeler le 911 ou les urgences immédiatement",
                "Ne pas conduire soi-même",
                "Suivre les instructions de l'opérateur",
                "Avoir les informations médicales prêtes"
            ],
            "urgent": [
                "⚠️ Consulter un médecin dans les 2-4 heures",
                "Aller à une clinique sans rendez-vous ou urgences",
                "Surveiller l'évolution des symptômes",
                "Préparer liste de médicaments actuels"
            ],
            "routine": [
                "Prendre rendez-vous avec médecin traitant",
                "Surveiller symptômes pendant 24-48h",
                "Noter évolution des symptômes",
                "Consulter si aggravation"
            ]
        }
        
        priority_colors = {
            "emergency": "🔴 ROUGE - URGENCE VITALE",
            "urgent": "🟠 ORANGE - URGENT",
            "routine": "🟢 VERT - NON-URGENT"
        }
        
        return {
            "success": True,
            "message": "Emergency triage completed with REAL medical AI",
            "urgency": urgency,
            "priority": priority_colors.get(urgency, "UNKNOWN"),
            "severity_score": severity,
            "recommended_actions": actions.get(urgency, []),
            "medical_analysis": analysis_data.get("medical_analysis", ""),
            "categories": analysis_data.get("categories", {}),
            "red_flags": analysis_data.get("red_flags", []),
            "vital_signs": vital_signs or {},
            "disclaimer": "⚠️ Ceci est une évaluation IA, pas un diagnostic médical. En cas de doute, consultez un professionnel ou appelez le 911.",
            "provider": "AI Leader Medical (Internal - FREE)",
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur triage: {str(e)}")
