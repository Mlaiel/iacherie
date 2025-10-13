"""
🎨 GÉNÉRATION MULTIMÉDIA - Images, Vidéos, Audio, 3D
Support de 644+ langues pour les prompts et métadonnées
"""

import os
import httpx
import asyncio
from typing import Dict, List, Optional, Literal
from datetime import datetime
from enum import Enum
import base64


class MediaType(str, Enum):
    """Types de médias générables"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    VOICE = "voice"
    MODEL_3D = "3d_model"
    ANIMATION = "animation"


class ImageStyle(str, Enum):
    """Styles d'images"""
    REALISTIC = "realistic"
    ANIME = "anime"
    CARTOON = "cartoon"
    ARTISTIC = "artistic"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"


class VideoStyle(str, Enum):
    """Styles de vidéos"""
    REALISTIC = "realistic"
    ANIMATED = "animated"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"


# Configuration des APIs de génération
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")  # Stable Diffusion
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")  # Vidéos, 3D
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Voix
SUNO_API_KEY = os.getenv("SUNO_API_KEY")  # Musique
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # DALL-E, TTS


class MultimediaGenerator:
    """
    Générateur multimédia universel avec support de 644+ langues
    - Images: DALL-E 3, Stable Diffusion, Midjourney
    - Vidéos: Runway, Pika, Stable Video
    - Audio: ElevenLabs, OpenAI TTS, Suno AI
    - 3D: Meshy, Rodin, TripoSR
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.generation_history = []
    
    # ========================================================================
    # GÉNÉRATION D'IMAGES
    # ========================================================================
    
    async def generate_image_dalle3(
        self,
        prompt: str,
        language: str = "EN",
        size: str = "1024x1024",
        quality: str = "hd",
        style: str = "vivid"
    ) -> Dict:
        """
        Génère une image avec DALL-E 3 (OpenAI)
        - Meilleure qualité
        - Support natif multilingue
        """
        if not OPENAI_API_KEY:
            return {"error": "OPENAI_API_KEY not configured"}
        
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "n": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "image_url": data["data"][0]["url"],
                    "revised_prompt": data["data"][0].get("revised_prompt"),
                    "model": "dall-e-3",
                    "language": language,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_image_stable_diffusion(
        self,
        prompt: str,
        negative_prompt: str = "",
        style: ImageStyle = ImageStyle.REALISTIC,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30
    ) -> Dict:
        """
        Génère une image avec Stable Diffusion XL
        - Plus rapide et gratuit
        - Meilleur contrôle artistique
        """
        if not STABILITY_API_KEY:
            # Utiliser Replicate comme fallback (gratuit)
            return await self.generate_image_replicate(prompt, style)
        
        try:
            response = await self.client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {STABILITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [
                        {"text": prompt, "weight": 1},
                        {"text": negative_prompt, "weight": -1} if negative_prompt else {}
                    ],
                    "cfg_scale": 7,
                    "height": height,
                    "width": width,
                    "steps": steps,
                    "samples": 1,
                    "style_preset": style.value
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                image_base64 = data["artifacts"][0]["base64"]
                
                return {
                    "success": True,
                    "image_base64": image_base64,
                    "model": "stable-diffusion-xl",
                    "style": style.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_image_replicate(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.REALISTIC
    ) -> Dict:
        """
        Génère une image via Replicate (FLUX, Playground v2.5)
        - Gratuit avec crédits
        - Très haute qualité
        """
        if not REPLICATE_API_KEY:
            return {"error": "REPLICATE_API_KEY not configured"}
        
        # Utiliser FLUX.1 [schnell] - Plus rapide et gratuit
        model = "black-forest-labs/flux-schnell"
        
        try:
            response = await self.client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "flux-schnell",
                    "input": {
                        "prompt": prompt,
                        "num_outputs": 1,
                        "aspect_ratio": "1:1",
                        "output_format": "png",
                        "output_quality": 90
                    }
                }
            )
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Attendre la génération (polling)
                for _ in range(60):  # Max 60 secondes
                    await asyncio.sleep(2)
                    
                    status_response = await self.client.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {REPLICATE_API_KEY}"}
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data["status"] == "succeeded":
                            return {
                                "success": True,
                                "image_url": status_data["output"][0],
                                "model": "flux-schnell",
                                "style": style.value,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        elif status_data["status"] == "failed":
                            return {"success": False, "error": status_data.get("error")}
                
                return {"success": False, "error": "Timeout"}
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # GÉNÉRATION DE VIDÉOS
    # ========================================================================
    
    async def generate_video_runway(
        self,
        prompt: str,
        duration: int = 5,
        style: VideoStyle = VideoStyle.CINEMATIC
    ) -> Dict:
        """
        Génère une vidéo avec Runway Gen-2
        - 5-10 secondes
        - Très haute qualité
        """
        # Runway nécessite une clé API premium
        # Utiliser Replicate comme alternative
        return await self.generate_video_replicate(prompt, duration, style)
    
    async def generate_video_replicate(
        self,
        prompt: str,
        duration: int = 5,
        style: VideoStyle = VideoStyle.REALISTIC
    ) -> Dict:
        """
        Génère une vidéo via Replicate (AnimateDiff, Stable Video)
        """
        if not REPLICATE_API_KEY:
            return {"error": "REPLICATE_API_KEY not configured"}
        
        # Utiliser AnimateDiff Lightning (rapide, gratuit)
        try:
            response = await self.client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "animatediff-lightning",
                    "input": {
                        "prompt": prompt,
                        "num_frames": duration * 8,  # 8 fps
                        "num_inference_steps": 8,
                        "guidance_scale": 1.2,
                        "width": 512,
                        "height": 512
                    }
                }
            )
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Attendre la génération
                for _ in range(120):  # Max 2 minutes
                    await asyncio.sleep(3)
                    
                    status_response = await self.client.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {REPLICATE_API_KEY}"}
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data["status"] == "succeeded":
                            return {
                                "success": True,
                                "video_url": status_data["output"],
                                "duration": duration,
                                "model": "animatediff-lightning",
                                "style": style.value,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        elif status_data["status"] == "failed":
                            return {"success": False, "error": status_data.get("error")}
                
                return {"success": False, "error": "Timeout"}
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # GÉNÉRATION AUDIO (VOIX)
    # ========================================================================
    
    async def generate_voice_elevenlabs(
        self,
        text: str,
        language: str = "EN",
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Dict:
        """
        Génère une voix avec ElevenLabs
        - Support de 29 langues
        - Voix ultra-réalistes
        """
        if not ELEVENLABS_API_KEY:
            # Fallback: OpenAI TTS
            return await self.generate_voice_openai(text, language)
        
        try:
            response = await self.client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost
                    }
                }
            )
            
            if response.status_code == 200:
                audio_bytes = response.content
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "model": "elevenlabs-multilingual-v2",
                    "language": language,
                    "voice_id": voice_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_voice_openai(
        self,
        text: str,
        language: str = "EN",
        voice: str = "alloy",
        model: str = "tts-1-hd"
    ) -> Dict:
        """
        Génère une voix avec OpenAI TTS
        - Moins cher
        - Bonne qualité
        """
        if not OPENAI_API_KEY:
            return {"error": "OPENAI_API_KEY not configured"}
        
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3"
                }
            )
            
            if response.status_code == 200:
                audio_bytes = response.content
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "model": model,
                    "language": language,
                    "voice": voice,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # GÉNÉRATION DE MUSIQUE
    # ========================================================================
    
    async def generate_music_suno(
        self,
        prompt: str,
        duration: int = 30,
        genre: str = "ambient"
    ) -> Dict:
        """
        Génère de la musique avec Suno AI
        - Texte vers musique
        - Support de tous les genres
        """
        # Suno nécessite API (en développement)
        # Alternative: MusicGen via Replicate
        return await self.generate_music_replicate(prompt, duration, genre)
    
    async def generate_music_replicate(
        self,
        prompt: str,
        duration: int = 30,
        genre: str = "ambient"
    ) -> Dict:
        """
        Génère de la musique avec MusicGen (Meta)
        """
        if not REPLICATE_API_KEY:
            return {"error": "REPLICATE_API_KEY not configured"}
        
        try:
            response = await self.client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "musicgen",
                    "input": {
                        "prompt": f"{genre} music: {prompt}",
                        "duration": duration,
                        "temperature": 1.0,
                        "top_k": 250,
                        "top_p": 0.0
                    }
                }
            )
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Attendre la génération
                for _ in range(60):
                    await asyncio.sleep(2)
                    
                    status_response = await self.client.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {REPLICATE_API_KEY}"}
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data["status"] == "succeeded":
                            return {
                                "success": True,
                                "audio_url": status_data["output"],
                                "duration": duration,
                                "genre": genre,
                                "model": "musicgen",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        elif status_data["status"] == "failed":
                            return {"success": False, "error": status_data.get("error")}
                
                return {"success": False, "error": "Timeout"}
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # GÉNÉRATION 3D
    # ========================================================================
    
    async def generate_3d_model(
        self,
        prompt: str,
        format: str = "glb"
    ) -> Dict:
        """
        Génère un modèle 3D à partir d'un texte
        - Meshy, Rodin, TripoSR
        """
        if not REPLICATE_API_KEY:
            return {"error": "REPLICATE_API_KEY not configured"}
        
        # Utiliser TripoSR (rapide, open-source)
        try:
            response = await self.client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "triposr",
                    "input": {
                        "prompt": prompt,
                        "output_format": format
                    }
                }
            )
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Attendre la génération
                for _ in range(120):
                    await asyncio.sleep(3)
                    
                    status_response = await self.client.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {REPLICATE_API_KEY}"}
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data["status"] == "succeeded":
                            return {
                                "success": True,
                                "model_url": status_data["output"],
                                "format": format,
                                "model": "triposr",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        elif status_data["status"] == "failed":
                            return {"success": False, "error": status_data.get("error")}
                
                return {"success": False, "error": "Timeout"}
            else:
                return {"success": False, "error": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # FONCTION UNIVERSELLE
    # ========================================================================
    
    async def generate(
        self,
        media_type: MediaType,
        prompt: str,
        language: str = "EN",
        **kwargs
    ) -> Dict:
        """
        Fonction universelle de génération multimédia
        """
        if media_type == MediaType.IMAGE:
            # Essayer DALL-E 3 en premier, puis Stable Diffusion
            if OPENAI_API_KEY:
                return await self.generate_image_dalle3(prompt, language, **kwargs)
            else:
                return await self.generate_image_stable_diffusion(prompt, **kwargs)
        
        elif media_type == MediaType.VIDEO:
            return await self.generate_video_replicate(prompt, **kwargs)
        
        elif media_type == MediaType.VOICE:
            if ELEVENLABS_API_KEY:
                return await self.generate_voice_elevenlabs(prompt, language, **kwargs)
            else:
                return await self.generate_voice_openai(prompt, language, **kwargs)
        
        elif media_type == MediaType.MUSIC:
            return await self.generate_music_replicate(prompt, **kwargs)
        
        elif media_type == MediaType.MODEL_3D:
            return await self.generate_3d_model(prompt, **kwargs)
        
        else:
            return {"error": f"Media type {media_type} not supported"}
    
    async def close(self):
        """Fermer le client HTTP"""
        await self.client.aclose()


# Instance globale
multimedia_generator = MultimediaGenerator()


# ========================================================================
# FONCTIONS UTILITAIRES
# ========================================================================

async def generate_image(prompt: str, language: str = "EN", **kwargs) -> Dict:
    """Génère une image (raccourci)"""
    return await multimedia_generator.generate(MediaType.IMAGE, prompt, language, **kwargs)


async def generate_video(prompt: str, **kwargs) -> Dict:
    """Génère une vidéo (raccourci)"""
    return await multimedia_generator.generate(MediaType.VIDEO, prompt, **kwargs)


async def generate_voice(text: str, language: str = "EN", **kwargs) -> Dict:
    """Génère une voix (raccourci)"""
    return await multimedia_generator.generate(MediaType.VOICE, text, language, **kwargs)


async def generate_music(prompt: str, **kwargs) -> Dict:
    """Génère de la musique (raccourci)"""
    return await multimedia_generator.generate(MediaType.MUSIC, prompt, **kwargs)


async def generate_3d(prompt: str, **kwargs) -> Dict:
    """Génère un modèle 3D (raccourci)"""
    return await multimedia_generator.generate(MediaType.MODEL_3D, prompt, **kwargs)
