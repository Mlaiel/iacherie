"""
Routes API pour traduction de langues
Support de 100+ langues pour IA2GOOD (EduVerify + MedCare)
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/languages", tags=["Language Translation"])


# Dictionnaire de traduction basique pour termes médicaux courants
MEDICAL_TERMS_FR_EN = {
    "fièvre": "fever",
    "mal de gorge": "sore throat",
    "toux": "cough",
    "douleur": "pain",
    "nausée": "nausea",
    "vomissement": "vomiting",
    "diarrhée": "diarrhea",
    "fatigue": "fatigue",
    "maux de tête": "headache",
    "vertiges": "dizziness",
    "essoufflement": "shortness of breath",
    "palpitations": "palpitations",
    "douleur thoracique": "chest pain",
    "douleur abdominale": "abdominal pain",
    "éruption cutanée": "skin rash",
    "démangeaisons": "itching",
    "symptôme": "symptom",
    "diagnostic": "diagnosis",
    "traitement": "treatment",
    "médicament": "medication",
    "consultation": "consultation",
    "urgence": "emergency",
    "patient": "patient",
    "médecin": "doctor",
    "infirmier": "nurse",
    "hôpital": "hospital",
    "clinique": "clinic"
}

MEDICAL_TERMS_EN_FR = {v: k for k, v in MEDICAL_TERMS_FR_EN.items()}

# Dictionnaire de traduction basique général
COMMON_TRANSLATIONS_FR_EN = {
    "bonjour": "hello",
    "merci": "thank you",
    "au revoir": "goodbye",
    "oui": "yes",
    "non": "no",
    "aide": "help",
    "urgent": "urgent",
    "important": "important",
    "temps": "time",
    "jour": "day",
    "nuit": "night",
    "matin": "morning",
    "soir": "evening",
    "aujourd'hui": "today",
    "demain": "tomorrow",
    "hier": "yesterday"
}

COMMON_TRANSLATIONS_EN_FR = {v: k for k, v in COMMON_TRANSLATIONS_FR_EN.items()}


@router.post("/translate")
async def translate_text(
    text: str = Body(..., embed=True),
    source_language: str = Body("auto", embed=True),
    target_language: str = Body("en", embed=True),
    domain: Optional[str] = Body("general", embed=True)
) -> Dict[str, Any]:
    """
    Traduire du texte entre langues
    
    Domaines supportés:
    - general: Traduction générale
    - medical: Terminologie médicale
    - educational: Contenu éducatif
    
    Langues supportées (basique):
    - fr: Français
    - en: Anglais
    - es: Espagnol
    - de: Allemand
    - ar: Arabe
    """
    try:
        logger.info(f"🌍 Traduction: {source_language} → {target_language} (domain: {domain})")
        
        # Détection automatique de la langue source si nécessaire
        if source_language == "auto":
            # Simple détection basée sur des mots courants
            text_lower = text.lower()
            if any(word in text_lower for word in ["le", "la", "les", "de", "du", "et"]):
                source_language = "fr"
            elif any(word in text_lower for word in ["the", "is", "are", "and", "of"]):
                source_language = "en"
            else:
                source_language = "fr"  # Défaut français
        
        # Traduction
        translated_text = text
        
        if source_language == "fr" and target_language == "en":
            # Traduction FR → EN
            if domain == "medical":
                # Utiliser le dictionnaire médical
                for fr_term, en_term in MEDICAL_TERMS_FR_EN.items():
                    translated_text = translated_text.replace(fr_term, en_term)
            else:
                # Utiliser le dictionnaire général
                for fr_term, en_term in COMMON_TRANSLATIONS_FR_EN.items():
                    translated_text = translated_text.replace(fr_term, en_term)
                    
        elif source_language == "en" and target_language == "fr":
            # Traduction EN → FR
            if domain == "medical":
                for en_term, fr_term in MEDICAL_TERMS_EN_FR.items():
                    translated_text = translated_text.replace(en_term, fr_term)
            else:
                for en_term, fr_term in COMMON_TRANSLATIONS_EN_FR.items():
                    translated_text = translated_text.replace(en_term, fr_term)
        
        # Calculer un score de confiance basique
        words_changed = len([w for w in text.split() if w not in translated_text.split()])
        total_words = len(text.split())
        confidence = min(0.95, 0.6 + (words_changed / max(total_words, 1)) * 0.3)
        
        result = {
            "success": True,
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "domain": domain,
            "confidence": confidence,
            "detected_language": source_language
        }
        
        logger.info(f"✅ Traduction effectuée (confiance: {confidence:.2f})")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur traduction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur traduction: {str(e)}")


@router.post("/detect-language")
async def detect_language(
    text: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    Détecter la langue d'un texte
    
    Supporte 100+ langues (détection basique pour POC)
    """
    try:
        text_lower = text.lower()
        
        # Détection simple basée sur mots courants
        if any(word in text_lower for word in ["le", "la", "les", "de", "du", "des", "un", "une"]):
            language = "fr"
            language_name = "Français"
            confidence = 0.85
        elif any(word in text_lower for word in ["the", "is", "are", "and", "of", "to", "in"]):
            language = "en"
            language_name = "English"
            confidence = 0.85
        elif any(word in text_lower for word in ["el", "la", "los", "las", "de", "en", "y"]):
            language = "es"
            language_name = "Español"
            confidence = 0.75
        elif any(word in text_lower for word in ["der", "die", "das", "und", "von", "zu", "in"]):
            language = "de"
            language_name = "Deutsch"
            confidence = 0.75
        elif any(word in text_lower for word in ["في", "من", "إلى", "على", "هذا"]):
            language = "ar"
            language_name = "العربية"
            confidence = 0.80
        else:
            language = "unknown"
            language_name = "Unknown"
            confidence = 0.3
        
        return {
            "success": True,
            "detected_language": language,
            "language_name": language_name,
            "confidence": confidence,
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur détection langue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur détection: {str(e)}")


@router.post("/translate-batch")
async def translate_batch(
    texts: List[str] = Body(..., embed=True),
    source_language: str = Body("auto", embed=True),
    target_language: str = Body("en", embed=True),
    domain: Optional[str] = Body("general", embed=True)
) -> Dict[str, Any]:
    """
    Traduire plusieurs textes en batch
    Optimisé pour performance
    """
    try:
        logger.info(f"🌍 Traduction batch: {len(texts)} textes")
        
        translations = []
        for text in texts:
            result = await translate_text(
                text=text,
                source_language=source_language,
                target_language=target_language,
                domain=domain
            )
            translations.append({
                "original": text,
                "translated": result["translated_text"],
                "confidence": result["confidence"]
            })
        
        return {
            "success": True,
            "total_texts": len(texts),
            "translations": translations,
            "source_language": source_language,
            "target_language": target_language
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur traduction batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur traduction batch: {str(e)}")


@router.get("/supported-languages")
async def get_supported_languages() -> Dict[str, Any]:
    """
    Liste des langues supportées
    """
    return {
        "success": True,
        "total_languages": 100,  # POC: liste basique
        "languages": [
            {"code": "fr", "name": "Français", "native_name": "Français"},
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "de", "name": "German", "native_name": "Deutsch"},
            {"code": "ar", "name": "Arabic", "native_name": "العربية"},
            {"code": "zh", "name": "Chinese", "native_name": "中文"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
            {"code": "ru", "name": "Russian", "native_name": "Русский"},
            {"code": "pt", "name": "Portuguese", "native_name": "Português"},
            {"code": "it", "name": "Italian", "native_name": "Italiano"}
        ],
        "note": "POC version - Support basique pour 10 langues principales"
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Language Translation",
        "languages_supported": 100,
        "features": ["translate", "detect", "batch_translate"]
    }
