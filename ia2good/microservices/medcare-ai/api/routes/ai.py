"""
Routes AI pour MedCare - Intégration avec IACherie
⚠️ DISCLAIMER: Assistance IA, PAS un diagnostic médical
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import sys
import os

# Add shared-services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared-services'))

try:
    from ai_orchestrator import get_orchestrator
    from iacherie_ai_client import get_ai_client, IAModelType
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

router = APIRouter(prefix="/ai", tags=["AI Integration - MedCare"])


# =============================================
# MEDICAL DISCLAIMER
# =============================================

MEDICAL_DISCLAIMER = """
⚠️ AVERTISSEMENT MÉDICAL IMPORTANT:
Cette assistance est fournie par une intelligence artificielle et NE CONSTITUE PAS
un diagnostic médical professionnel. Les informations fournies sont uniquement à
titre informatif. Pour tout problème de santé, consultez TOUJOURS un médecin
qualifié ou un professionnel de santé agréé.

En cas d'urgence médicale, contactez immédiatement les services d'urgence (112/15).
"""


# =============================================
# PYDANTIC MODELS
# =============================================

class SymptomAnalysisRequest(BaseModel):
    symptoms_description: str
    language: str = "fr"
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    existing_conditions: Optional[List[str]] = []


class MedicalTermTranslationRequest(BaseModel):
    medical_terms: List[str]
    target_language: str


# =============================================
# CONSULTATION TRANSCRIPTION
# =============================================

@router.post("/transcribe-consultation")
async def transcribe_medical_consultation(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("fr")
):
    """
    Transcrire consultation médicale audio
    
    Utilise: Whisper Large
    Priority: HIGH (IA2GOOD humanitaire gratuit)
    
    Use case: Telemedicine, consultation documentation
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        # Read audio file
        audio_bytes = await audio_file.read()
        
        # Call IACherie Whisper model
        orchestrator = get_orchestrator()
        result = await orchestrator.medcare_transcribe_consultation(
            audio_file=audio_bytes,
            language=language
        )
        
        return {
            "success": True,
            "transcription": result.get("text", ""),
            "language_detected": result.get("language", language),
            "medical_analysis": result.get("medical_analysis", {}),
            "disclaimer": MEDICAL_DISCLAIMER
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# =============================================
# SYMPTOM ANALYSIS
# =============================================

@router.post("/analyze-symptoms")
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyser symptômes avec IA médicale
    
    Utilise: AI Leader GPT-XL (medical context) + Content Classification
    Priority: HIGH
    
    ⚠️ IMPORTANT: Ceci est une ASSISTANCE, PAS un diagnostic médical!
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.medcare_analyze_symptoms(
            symptoms_description=request.symptoms_description,
            language=request.language
        )
        
        return {
            "success": True,
            "symptoms": request.symptoms_description,
            "analysis": result.get("analysis", ""),
            "urgency_level": result.get("urgency", "unknown"),
            "language": request.language,
            "patient_info": {
                "age": request.patient_age,
                "sex": request.patient_sex,
                "existing_conditions": request.existing_conditions
            },
            "disclaimer": result.get("disclaimer", MEDICAL_DISCLAIMER),
            "recommendations": [
                "Consultez un médecin pour un diagnostic professionnel",
                "Si urgence: appelez le 15 (France) ou 112 (Europe)",
                "Cette analyse est uniquement informative"
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Symptom analysis failed: {str(e)}")


# =============================================
# VOICE ADVICE (TTS)
# =============================================

@router.post("/generate-voice-advice")
async def generate_voice_medical_advice(
    medical_advice: str,
    language: str = "fr",
    voice: str = "medical_professional"
):
    """
    Générer recommandations médicales en audio (TTS)
    
    Utilise: TTS Pro / Voice XL
    Priority: HIGH
    
    Use case: Accessibilité (patients malvoyants), elderly care
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        audio = await orchestrator.medcare_generate_voice_advice(
            medical_advice=medical_advice,
            language=language,
            voice=voice
        )
        
        return {
            "success": True,
            "audio_url": audio.get("audio_url"),
            "text": medical_advice,
            "language": language,
            "duration": audio.get("duration", 0),
            "disclaimer": MEDICAL_DISCLAIMER
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")


# =============================================
# MEDICAL TERM TRANSLATION
# =============================================

@router.post("/translate-medical-terms")
async def translate_medical_terminology(request: MedicalTermTranslationRequest):
    """
    Traduire terminologie médicale
    
    Utilise: Translation model (specialized medical)
    Priority: HIGH
    
    Use case: Multilingual consultations, refugee care
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        translations = await orchestrator.medcare_translate_medical_terms(
            medical_terms=request.medical_terms,
            target_language=request.target_language
        )
        
        return {
            "success": True,
            "source_language": "en",  # Medical terms usually in English
            "target_language": request.target_language,
            "translations": translations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# =============================================
# SPECIALIST RECOMMENDATION
# =============================================

@router.post("/recommend-specialists")
async def recommend_medical_specialists(
    symptoms: str,
    location: Dict[str, float],  # {"latitude": 48.8566, "longitude": 2.3522}
    language: str = "fr",
    insurance_type: Optional[str] = None
):
    """
    Recommander spécialistes médicaux appropriés
    
    Utilise: User Recommendation model + Geolocation
    Priority: HIGH
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        orchestrator = get_orchestrator()
        recommendations = await orchestrator.medcare_recommend_specialists(
            symptoms=symptoms,
            location=location,
            user_profile={
                "language": language,
                "insurance": insurance_type
            }
        )
        
        return {
            "success": True,
            "symptoms": symptoms,
            "location": location,
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


# =============================================
# HEALTH EDUCATION
# =============================================

@router.post("/generate-health-education")
async def generate_health_education_content(
    topic: str,
    target_audience: str = "general",  # general, children, elderly
    language: str = "fr"
):
    """
    Générer contenu éducatif santé
    
    Utilise: AI Leader GPT-XL
    Priority: HIGH
    
    Topics: nutrition, hygiene, disease prevention, mental health, etc.
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        client = get_ai_client()
        
        prompt = f"""
        Génère un contenu éducatif en santé sur le sujet: {topic}
        Public cible: {target_audience}
        Langue: {language}
        
        Le contenu doit être:
        - Accessible et compréhensible
        - Basé sur des faits médicaux vérifiés
        - Adapté au public cible
        - Positif et encourageant
        - Avec des conseils pratiques
        
        Format: Introduction, Points clés, Conseils pratiques, Conclusion
        """
        
        result = await client.generate_text(
            prompt=prompt,
            model=IAModelType.AI_LEADER_GPT_XL,
            max_tokens=800,
            system_prompt="Tu es un éducateur en santé. Fournis des informations médicales précises, accessibles et vérifiées."
        )
        
        return {
            "success": True,
            "topic": topic,
            "target_audience": target_audience,
            "language": language,
            "content": result.get("text", ""),
            "disclaimer": "Informations à but éducatif uniquement. Consultez un professionnel de santé pour des conseils médicaux personnalisés."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


# =============================================
# EMERGENCY DETECTION
# =============================================

@router.post("/detect-emergency")
async def detect_medical_emergency(
    symptoms: str,
    language: str = "fr"
):
    """
    Détecter urgence médicale dans description de symptômes
    
    Utilise: Content Classification model
    Priority: CRITICAL
    
    Returns: urgency level (critical/emergency/urgent/moderate/minor)
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        client = get_ai_client()
        
        result = await client.classify_content(
            content=symptoms,
            categories=[
                "critical_emergency",  # Danger de mort immédiat
                "emergency",           # Urgence vitale
                "urgent",              # Consulter rapidement
                "moderate",            # Consulter sous quelques jours
                "minor"                # Non urgent
            ]
        )
        
        urgency = result.get("category", "unknown")
        confidence = result.get("confidence", 0)
        
        # Déterminer le message d'urgence
        if urgency in ["critical_emergency", "emergency"]:
            message = "🚨 URGENCE MÉDICALE DÉTECTÉE - Appelez le 15 (France) ou 112 (Europe) IMMÉDIATEMENT"
            action = "call_emergency"
        elif urgency == "urgent":
            message = "⚠️ Consultez un médecin dans les 24 heures"
            action = "consult_soon"
        elif urgency == "moderate":
            message = "📅 Prenez rendez-vous avec votre médecin cette semaine"
            action = "schedule_appointment"
        else:
            message = "ℹ️ Symptômes mineurs - Surveillez l'évolution"
            action = "monitor"
        
        return {
            "success": True,
            "symptoms": symptoms,
            "urgency_level": urgency,
            "confidence": confidence,
            "message": message,
            "recommended_action": action,
            "emergency_numbers": {
                "france": "15",
                "europe": "112",
                "international": "+33-15"
            },
            "disclaimer": MEDICAL_DISCLAIMER
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency detection failed: {str(e)}")


# =============================================
# MEDICATION INFORMATION
# =============================================

@router.post("/medication-info")
async def get_medication_information(
    medication_name: str,
    language: str = "fr"
):
    """
    Obtenir informations sur un médicament
    
    Utilise: AI Leader GPT-XL (medical database)
    Priority: HIGH
    
    ⚠️ Informations à but informatif uniquement
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        client = get_ai_client()
        
        prompt = f"""
        Fournis des informations sur le médicament: {medication_name}
        Langue: {language}
        
        Informations à inclure:
        - Nom générique et commercial
        - Usage principal
        - Dosage habituel (général)
        - Effets secondaires courants
        - Précautions importantes
        - Interactions médicamenteuses majeures
        
        ⚠️ IMPORTANT: Rappelle que c'est informatif et que le patient doit suivre
        les prescriptions de son médecin.
        """
        
        result = await client.generate_text(
            prompt=prompt,
            model=IAModelType.AI_LEADER_GPT_XL,
            max_tokens=600,
            system_prompt="Tu es un pharmacien assistant. Fournis des informations précises sur les médicaments mais rappelle toujours de suivre les prescriptions médicales."
        )
        
        return {
            "success": True,
            "medication_name": medication_name,
            "language": language,
            "information": result.get("text", ""),
            "disclaimer": "Ces informations sont à titre informatif uniquement. Suivez TOUJOURS les prescriptions de votre médecin ou pharmacien. Ne modifiez jamais votre traitement sans avis médical."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medication info failed: {str(e)}")


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
            "module": "medcare",
            "iacherie_api": health,
            "disclaimer": MEDICAL_DISCLAIMER
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
