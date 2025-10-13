"""
Service d'orchestration IA pour IA2GOOD
Intégration avec les 27 modèles IA de IACherie
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from iacherie_ai_client import get_ai_client, IAModelType


class IA2GOODModule(str, Enum):
    """Modules IA2GOOD"""
    GUARDIAN = "guardian"          # Volunteer matching / humanitarian
    EDUVERIFY = "eduverify"        # Educational verification
    MEDCARE = "medcare"            # Medical AI assistance


class AIOrchestrator:
    """
    Orchestrateur IA pour IA2GOOD
    Simplifie l'utilisation des modèles IACherie pour chaque module
    """
    
    def __init__(self):
        self.client = get_ai_client()
    
    # =============================================
    # GUARDIAN MODULE - Volunteer Matching
    # =============================================
    
    async def guardian_transcribe_testimony(
        self,
        audio_file: bytes,
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Transcrire témoignage humanitaire (audio → texte)
        Utilise: Whisper Large (100+ langues)
        """
        result = await self.client.transcribe_audio(
            audio_file=audio_file,
            model=IAModelType.WHISPER_LARGE,
            language=language
        )
        
        # Catégoriser le témoignage
        if result.get("text"):
            classification = await self.client.classify_content(
                content=result["text"],
                categories=[
                    "natural_disaster", "conflict", "health_crisis",
                    "education_need", "food_insecurity", "shelter"
                ]
            )
            result["category"] = classification
        
        return result
    
    async def guardian_generate_mission_description(
        self,
        mission_details: Dict[str, Any],
        language: str = "fr"
    ) -> str:
        """
        Générer description de mission humanitaire
        Utilise: AI Leader GPT-XL
        """
        prompt = f"""
        Génère une description engageante pour cette mission humanitaire:
        
        Type: {mission_details.get('type')}
        Localisation: {mission_details.get('location')}
        Durée: {mission_details.get('duration')}
        Compétences requises: {', '.join(mission_details.get('skills', []))}
        Contexte: {mission_details.get('context')}
        
        La description doit être:
        - Motivante pour les volontaires
        - Claire sur les besoins
        - Respectueuse des communautés locales
        - En {language}
        """
        
        result = await self.client.generate_text(
            prompt=prompt,
            model=IAModelType.AI_LEADER_GPT_XL,
            max_tokens=300
        )
        
        return result.get("text", "")
    
    async def guardian_match_volunteers(
        self,
        mission: Dict[str, Any],
        volunteers_pool: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Matcher volontaires avec missions
        Utilise: User Recommendation model
        """
        recommendations = await self.client.get_recommendations(
            user_profile={
                "type": "mission",
                "mission_details": mission
            },
            context="volunteer_matching",
            limit=len(volunteers_pool)
        )
        
        return recommendations.get("recommendations", [])
    
    async def guardian_translate_multilingual(
        self,
        text: str,
        target_languages: List[str]
    ) -> Dict[str, str]:
        """
        Traduire contenu en plusieurs langues (réfugiés, international)
        Utilise: Translation model
        """
        translations = {}
        
        tasks = [
            self.client.translate_text(text, target_lang)
            for target_lang in target_languages
        ]
        
        results = await asyncio.gather(*tasks)
        
        for lang, result in zip(target_languages, results):
            translations[lang] = result.get("translated_text", "")
        
        return translations
    
    # =============================================
    # EDUVERIFY MODULE - Educational Content
    # =============================================
    
    async def eduverify_fact_check_content(
        self,
        educational_content: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Vérifier contenu éducatif (fact-checking)
        Utilise: Content Classification + Fact Check
        """
        # Vérification des faits
        fact_check = await self.client.fact_check(
            content=educational_content,
            sources=sources or ["wikipedia", "duckduckgo", "scholarly"]
        )
        
        # Évaluation de qualité
        quality = await self.client.assess_quality(
            content=educational_content,
            content_type="educational"
        )
        
        # ✅ CORRECTION: Utiliser les bonnes clés retournées par l'API
        return {
            "fact_check": fact_check,
            "quality_score": quality.get("overall_score", 0),  # ← Corrigé: overall_score au lieu de score
            "recommendations": quality.get("recommendations", []),  # ← Corrigé: recommendations au lieu de improvements
            "verified": fact_check.get("verified", False)
        }
    
    async def eduverify_generate_summary(
        self,
        educational_content: str,
        target_level: str = "high_school"
    ) -> str:
        """
        Générer résumé de contenu éducatif
        Utilise: AI Leader GPT-XL
        """
        prompt = f"""
        Résume ce contenu éducatif pour un niveau {target_level}:
        
        {educational_content}
        
        Le résumé doit:
        - Capturer les concepts clés
        - Être accessible au niveau {target_level}
        - Être structuré et clair
        - Inclure exemples si pertinent
        """
        
        result = await self.client.generate_text(
            prompt=prompt,
            model=IAModelType.TEXT_PRO,
            max_tokens=400
        )
        
        return result.get("text", "")
    
    async def eduverify_generate_quiz(
        self,
        educational_content: str,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Générer quiz à partir de contenu éducatif
        Utilise: AI Leader GPT-XL
        """
        prompt = f"""
        Génère {num_questions} questions QCM basées sur ce contenu:
        
        {educational_content}
        
        Format pour chaque question:
        - Question claire
        - 4 options (A, B, C, D)
        - Réponse correcte
        - Explication courte
        """
        
        result = await self.client.generate_text(
            prompt=prompt,
            model=IAModelType.AI_LEADER_GPT_XL,
            max_tokens=800
        )
        
        # Parse le résultat (à améliorer avec structured output)
        return {"quiz_raw": result.get("text", "")}
    
    async def eduverify_optimize_seo(
        self,
        educational_content: str,
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Optimiser contenu éducatif pour SEO
        Utilise: SEO Optimization model
        """
        # Note: À implémenter côté IACherie API
        result = await self.client.client.post("/api/v1/seo/optimize", json={
            "content": educational_content,
            "keywords": target_keywords,
            "content_type": "educational"
        })
        
        return result.json()
    
    # =============================================
    # MEDCARE MODULE - Medical AI
    # =============================================
    
    async def medcare_transcribe_consultation(
        self,
        audio_file: bytes,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Transcrire consultation médicale
        Utilise: Whisper Large
        """
        transcription = await self.client.transcribe_audio(
            audio_file=audio_file,
            model=IAModelType.WHISPER_LARGE,
            language=language
        )
        
        # Extraire symptômes et diagnostic (avec LLM)
        if transcription.get("text"):
            analysis = await self.medcare_analyze_symptoms(
                transcription["text"],
                language=language
            )
            transcription["medical_analysis"] = analysis
        
        return transcription
    
    async def medcare_analyze_symptoms(
        self,
        symptoms_description: str,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Analyser symptômes avec IA médicale
        Utilise: AI Leader GPT-XL (medical context)
        
        ⚠️ DISCLAIMER: Ceci est une assistance, pas un diagnostic médical
        """
        # Traduire en anglais si nécessaire (meilleur corpus médical)
        if language != "en":
            translated = await self.client.translate_text(
                text=symptoms_description,
                target_language="en",
                source_language=language
            )
            symptoms_en = translated.get("translated_text", symptoms_description)
        else:
            symptoms_en = symptoms_description
        
        prompt = f"""
        You are a medical AI assistant. Analyze these symptoms:
        
        {symptoms_en}
        
        Provide:
        1. Possible conditions (most to least likely)
        2. Severity assessment (urgent, moderate, minor)
        3. Recommended actions
        4. Red flags to watch for
        
        IMPORTANT: This is NOT a medical diagnosis. Patient should consult a licensed physician.
        """
        
        result = await self.client.generate_text(
            prompt=prompt,
            model=IAModelType.AI_LEADER_GPT_XL,
            max_tokens=600,
            system_prompt="You are a medical AI assistant. Always remind users this is not a replacement for professional medical advice."
        )
        
        analysis = result.get("text", "")
        
        # Re-traduire en langue originale
        if language != "en":
            retranslated = await self.client.translate_text(
                text=analysis,
                target_language=language,
                source_language="en"
            )
            analysis = retranslated.get("translated_text", analysis)
        
        # Classifier l'urgence
        urgency = await self.client.classify_content(
            content=symptoms_description,
            categories=["emergency", "urgent", "moderate", "minor"]
        )
        
        return {
            "analysis": analysis,
            "urgency": urgency.get("category", "unknown"),
            "language": language,
            "disclaimer": "Ceci est une assistance IA, pas un diagnostic médical. Consultez un médecin."
        }
    
    async def medcare_generate_voice_advice(
        self,
        medical_advice: str,
        language: str = "fr",
        voice: str = "medical_professional"
    ) -> Dict[str, Any]:
        """
        Générer recommandations médicales en audio
        Utilise: TTS Pro
        """
        audio = await self.client.text_to_speech(
            text=medical_advice,
            model=IAModelType.TTS_PRO,
            language=language,
            voice=voice
        )
        
        return audio
    
    async def medcare_translate_medical_terms(
        self,
        medical_terms: List[str],
        target_language: str
    ) -> Dict[str, str]:
        """
        Traduire terminologie médicale
        Utilise: Translation model (specialized medical)
        """
        translations = {}
        
        for term in medical_terms:
            result = await self.client.translate_text(
                text=term,
                target_language=target_language,
                source_language="en"
            )
            translations[term] = result.get("translated_text", term)
        
        return translations
    
    async def medcare_recommend_specialists(
        self,
        symptoms: str,
        location: Dict[str, float],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recommander spécialistes médicaux
        Utilise: User Recommendation model
        """
        recommendations = await self.client.get_recommendations(
            user_profile={
                "symptoms": symptoms,
                "location": location,
                "insurance": user_profile.get("insurance"),
                "language": user_profile.get("language", "fr")
            },
            context="medical_specialist_matching",
            limit=10
        )
        
        return recommendations.get("recommendations", [])
    
    # =============================================
    # SHARED UTILITIES
    # =============================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier que IACherie API est disponible"""
        return await self.client.health_check()
    
    async def close(self):
        """Cleanup"""
        await self.client.close()


# =============================================
# INSTANCE GLOBALE
# =============================================

_orchestrator: Optional[AIOrchestrator] = None

def get_orchestrator() -> AIOrchestrator:
    """
    Obtenir l'instance globale de l'orchestrateur
    
    Usage:
        from shared_services.ai_orchestrator import get_orchestrator
        
        orchestrator = get_orchestrator()
        result = await orchestrator.guardian_transcribe_testimony(audio_data)
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator


async def close_orchestrator():
    """Fermer l'orchestrateur"""
    global _orchestrator
    if _orchestrator is not None:
        await _orchestrator.close()
        _orchestrator = None
