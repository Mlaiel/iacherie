"""
Client d'intégration IA2GOOD ⟷ IACherie
Permet aux services IA2GOOD d'utiliser les 27 modèles IA de IACherie
"""

import httpx
import os
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio
from datetime import datetime


class IAModelType(str, Enum):
    """Types de modèles IA disponibles"""
    # Image Generation
    SDXL_TURBO = "sdxl-turbo"
    SD_TURBO = "sd-turbo"
    SD_15 = "sd-1.5"
    INTERNAL_IMAGE = "internal-image"
    
    # Text/LLM - UPDATED TO MATCH REAL MODELS
    AI_LEADER_GPT_XL = "internal-gpt-xl"       # FREE internal model
    TEXT_PRO = "internal-text-pro"             # FREE internal model
    CODE_WRITER = "internal-code-writer"       # FREE internal model
    
    # Audio
    VOICE_XL = "voice-xl"
    TTS_PRO = "tts-pro"
    MUSIC_GEN = "music-gen"
    VOICE_CLONE = "voice-clone"
    
    # Whisper (Transcription)
    WHISPER_TINY = "whisper-tiny"
    WHISPER_BASE = "whisper-base"
    WHISPER_SMALL = "whisper-small"
    WHISPER_MEDIUM = "whisper-medium"
    WHISPER_LARGE = "whisper-large"
    
    # Video
    VIDEO_TURBO = "video-turbo"
    VIDEO_PRO = "video-pro"
    VIDEO_XL = "video-xl"
    
    # 3D
    THREE_D_XL = "3d-xl"
    THREE_D_PRO = "3d-pro"
    MESH_GEN = "mesh-gen"
    
    # ML Pipeline
    CONTENT_CLASSIFICATION = "content-classification"
    USER_RECOMMENDATION = "user-recommendation"
    FRAUD_DETECTION = "fraud-detection"
    QUALITY_ASSESSMENT = "quality-assessment"
    SEO_OPTIMIZATION = "seo-optimization"


class IAcheriePriority(str, Enum):
    """Priorités pour les requêtes (IA2GOOD = haute priorité)"""
    HIGH = "high"      # IA2GOOD (humanitaire gratuit)
    NORMAL = "normal"  # IACherie (commercial payant)
    LOW = "low"        # Batch processing


class IAcherieAIClient:
    """
    Client pour appeler les modèles IA de IACherie depuis IA2GOOD
    
    Architecture:
    - IA2GOOD (humanitaire) → Priorité HAUTE (gratuit)
    - IACherie (commercial) → Priorité NORMALE (payant)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        source: str = "ia2good",
        timeout: float = 120.0
    ):
        self.base_url = base_url or os.getenv(
            "IACHERIE_API_URL",
            "http://iacherie-api-service:8000"
        )
        self.api_key = api_key or os.getenv("IACHERIE_API_KEY", "")
        self.source = source
        
        # Build headers only with non-None values
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.source:
            headers["X-Source"] = self.source
        headers["X-Priority"] = IAcheriePriority.HIGH.value  # IA2GOOD = priorité haute
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout
        )
    
    async def close(self):
        """Fermer la connexion HTTP"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    # =============================================
    # IMAGE GENERATION
    # =============================================
    
    async def generate_image(
        self,
        prompt: str,
        model: IAModelType = IAModelType.SDXL_TURBO,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: Optional[str] = None,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 4
    ) -> Dict[str, Any]:
        """
        Génération d'image via IACherie
        
        Use cases IA2GOOD:
        - Guardian: Illustrations pour campagnes humanitaires
        - EduVerify: Images éducatives
        - MedCare: Infographies médicales
        """
        response = await self.client.post("/api/generate/image", json={
            "prompt": prompt,
            "model": model.value,
            "width": width,
            "height": height,
            "negative_prompt": negative_prompt,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # TEXT GENERATION (LLM)
    # =============================================
    
    async def generate_text(
        self,
        prompt: str,
        model: IAModelType = IAModelType.AI_LEADER_GPT_XL,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génération de texte via LLM IACherie
        
        Use cases IA2GOOD:
        - Guardian: Descriptions de missions humanitaires
        - EduVerify: Résumés éducatifs, explications
        - MedCare: Recommandations médicales, conseils santé
        """
        response = await self.client.post("/api/generate/text", json={
            "prompt": prompt,
            "model": model.value,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system_prompt": system_prompt,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        result = response.json()
        
        # Extract data from wrapper if present
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return result
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: IAModelType = IAModelType.AI_LEADER_GPT_XL,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Chat completion (conversation multi-tours)
        
        Use cases IA2GOOD:
        - MedCare: Consultations médicales interactives
        - EduVerify: Tuteur éducatif conversationnel
        """
        response = await self.client.post("/api/ai/generate", json={
            "prompt": "\n".join([f"{m['role']}: {m['content']}" for m in messages]),
            "model": model.value,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # AUDIO (TTS, Voice Clone, Music)
    # =============================================
    
    async def text_to_speech(
        self,
        text: str,
        model: IAModelType = IAModelType.TTS_PRO,
        language: str = "fr",
        voice: str = "default"
    ) -> Dict[str, Any]:
        """
        Synthèse vocale
        
        Use cases IA2GOOD:
        - MedCare: Recommandations médicales audio
        - EduVerify: Contenu éducatif audio
        - Guardian: Messages d'urgence vocaux
        """
        response = await self.client.post("/api/languages/tts", json={
            "text": text,
            "voice": voice,
            "language": language,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    async def clone_voice(
        self,
        audio_sample: bytes,
        target_text: str,
        model: IAModelType = IAModelType.VOICE_CLONE
    ) -> Dict[str, Any]:
        """
        Clonage de voix
        
        Use cases IA2GOOD:
        - MedCare: Voix du médecin pour rassurer le patient
        """
        files = {"audio": ("sample.wav", audio_sample, "audio/wav")}
        data = {
            "target_text": target_text,
            "priority": IAcheriePriority.HIGH.value
        }
        response = await self.client.post("/api/studios/audio/clone-voice", files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # WHISPER (Transcription Audio → Text)
    # =============================================
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        model: IAModelType = IAModelType.WHISPER_LARGE,
        language: Optional[str] = None,
        task: str = "transcribe"  # transcribe | translate
    ) -> Dict[str, Any]:
        """
        Transcription audio via Whisper
        
        Use cases IA2GOOD:
        - Guardian: Transcription de témoignages (100+ langues)
        - MedCare: Transcription consultations médicales
        - EduVerify: Transcription cours audio
        """
        files = {"file": ("audio.mp3", audio_file, "audio/mpeg")}
        data = {
            "language": language or "auto",
            "task": task,
            "priority": IAcheriePriority.HIGH.value
        }
        response = await self.client.post("/api/languages/stt", files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # TRANSLATION (Multilangue)
    # =============================================
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Traduction multilingue (100+ langues)
        
        Use cases IA2GOOD:
        - Guardian: Traduction missions humanitaires
        - MedCare: Traduction consultations (réfugiés, migrants)
        - EduVerify: Traduction contenu éducatif
        """
        response = await self.client.post("/api/languages/translate", json={
            "text": text,
            "target_language": target_language,
            "source_language": source_language,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # CONTENT ANALYSIS (Classification, Fact-Checking)
    # =============================================
    
    async def classify_content(
        self,
        content: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Classification de contenu
        
        Use cases IA2GOOD:
        - Guardian: Catégorisation des besoins humanitaires
        - EduVerify: Classification contenu éducatif
        - MedCare: Triage symptômes (urgence/non-urgence)
        """
        response = await self.client.post("/api/ai-agents/text-analysis", json={
            "text": content,
            "analysis_type": "classification",
            "categories": categories,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    async def fact_check(
        self,
        content: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Vérification de faits (fact-checking)
        
        Use cases IA2GOOD:
        - EduVerify: Vérification contenu éducatif
        - MedCare: Vérification informations médicales
        """
        response = await self.client.post("/api/ai-agents/text-analysis", json={
            "text": content,
            "analysis_type": "fact_check",
            "sources": sources or ["wikipedia", "duckduckgo"],
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    async def assess_quality(
        self,
        content: str,
        content_type: str = "educational"
    ) -> Dict[str, Any]:
        """
        Évaluation de qualité
        
        Use cases IA2GOOD:
        - EduVerify: Qualité contenu éducatif
        - MedCare: Qualité informations médicales
        """
        response = await self.client.post("/api/ai-agents/text-analysis", json={
            "text": content,
            "analysis_type": "quality_assessment",
            "content_type": content_type,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # RECOMMENDATIONS
    # =============================================
    
    async def get_recommendations(
        self,
        user_profile: Dict[str, Any],
        context: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Recommandations personnalisées
        
        Use cases IA2GOOD:
        - Guardian: Matching volunteers avec missions
        - EduVerify: Recommandation ressources éducatives
        - MedCare: Recommandation médecins/spécialistes
        """
        response = await self.client.post("/api/ai-agents/text-analysis", json={
            "text": f"Context: {context}\nProfile: {user_profile}",
            "analysis_type": "recommendation",
            "limit": limit,
            "priority": IAcheriePriority.HIGH.value
        })
        response.raise_for_status()
        return response.json()
    
    # =============================================
    # BATCH PROCESSING (Plusieurs requêtes en parallèle)
    # =============================================
    
    async def batch_process(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Traitement par lots (optimisé pour IA2GOOD)
        
        Use cases IA2GOOD:
        - Guardian: Traitement masse de témoignages
        - EduVerify: Vérification masse de contenu
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_one(request: Dict[str, Any]):
            async with semaphore:
                method = request.get("method", "POST")
                endpoint = request["endpoint"]
                data = request.get("data", {})
                
                if method == "POST":
                    response = await self.client.post(endpoint, json=data)
                else:
                    response = await self.client.get(endpoint, params=data)
                
                response.raise_for_status()
                return response.json()
        
        tasks = [process_one(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    # =============================================
    # HEALTH CHECK
    # =============================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier que l'API IACherie est disponible"""
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "details": response.json()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# =============================================
# INSTANCE GLOBALE (Singleton)
# =============================================

_global_client: Optional[IAcherieAIClient] = None

def get_ai_client() -> IAcherieAIClient:
    """
    Obtenir l'instance globale du client IA
    
    Usage:
        from shared_services.iacherie_ai_client import get_ai_client
        
        ai_client = get_ai_client()
        result = await ai_client.generate_text("Hello world")
    """
    global _global_client
    if _global_client is None:
        # Essayer de récupérer l'URL depuis les variables d'environnement
        base_url = os.getenv("IACHERIE_API_URL", "http://localhost:8000")
        print(f"🔍 DEBUG get_ai_client: IACHERIE_API_URL={base_url}")
        _global_client = IAcherieAIClient(base_url=base_url)
        print(f"🔍 DEBUG client created: base_url={_global_client.base_url}, httpx base_url={_global_client.client.base_url}")
    return _global_client


async def close_ai_client():
    """Fermer l'instance globale (cleanup)"""
    global _global_client
    if _global_client is not None:
        await _global_client.close()
        _global_client = None
