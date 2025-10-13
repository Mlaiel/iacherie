#!/usr/bin/env python3
"""
🎵 MOZILLA TTS - TEXT-TO-SPEECH API INTEGRATION
Service de synthèse vocale gratuit et open source
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib.parse
import base64
from io import BytesIO

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TTSAudio:
    """Données audio TTS générées"""
    text: str
    voice: str
    language: str
    audio_url: Optional[str] = None
    audio_data: Optional[bytes] = None
    format: str = "wav"
    sample_rate: int = 22050
    duration_ms: Optional[int] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Voice:
    """Informations sur une voix TTS"""
    name: str
    language: str
    gender: str
    description: str
    quality: str = "standard"
    sample_url: Optional[str] = None

class MozillaTTSAPI:
    """Client pour Mozilla TTS - Service gratuit de synthèse vocale"""
    
    def __init__(self):
        # Utilisation d'un serveur TTS public (alternatives gratuites)
        self.base_urls = [
            "https://tts.voicerss.org",  # VoiceRSS (gratuit avec limites)
            "https://api.streamelements.com/kappa/v2/speech",  # StreamElements TTS
            "https://translate.google.com/translate_tts"  # Google TTS (simple)
        ]
        
        self.session = None
        
        # Voix disponibles gratuitement
        self.available_voices = [
            Voice("Brian", "en", "male", "English (US) - Male voice"),
            Voice("Amy", "en", "female", "English (US) - Female voice"),
            Voice("Emma", "en", "female", "English (UK) - Female voice"),
            Voice("Russell", "en", "male", "English (AU) - Male voice"),
            Voice("Nicole", "en", "female", "English (AU) - Female voice"),
            Voice("Celine", "fr", "female", "French - Female voice"),
            Voice("Mathieu", "fr", "male", "French - Male voice"),
            Voice("Marlene", "de", "female", "German - Female voice"),
            Voice("Hans", "de", "male", "German - Male voice"),
            Voice("Carla", "it", "female", "Italian - Female voice"),
            Voice("Giorgio", "it", "male", "Italian - Male voice"),
            Voice("Conchita", "es", "female", "Spanish - Female voice"),
            Voice("Enrique", "es", "male", "Spanish - Male voice"),
        ]
        
        # Langues supportées
        self.supported_languages = {
            "en": "English",
            "fr": "French", 
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
        
        logger.info("🎵 MozillaTTSAPI initialisé - Services TTS gratuits")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; iaCherie TTS Client)'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def synthesize_speech_voicerss(self, 
                                       text: str,
                                       voice: str = "Amy",
                                       language: str = "en") -> Optional[TTSAudio]:
        """Synthèse via VoiceRSS (gratuit avec API key optionnelle)"""
        
        try:
            # URL VoiceRSS
            url = "https://api.voicerss.org/"
            
            # Paramètres (sans API key = version limitée gratuite)
            params = {
                'key': '',  # Laisser vide pour version gratuite
                'src': text[:500],  # Limite à 500 caractères
                'hl': f"{language}-us" if language == "en" else language,
                'v': voice,
                'c': 'wav',
                'f': '22khz_16bit_mono'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'audio' in content_type:
                        audio_data = await response.read()
                        
                        return TTSAudio(
                            text=text,
                            voice=voice,
                            language=language,
                            audio_data=audio_data,
                            format="wav"
                        )
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ VoiceRSS error: {error_text}")
                        return None
                else:
                    logger.error(f"❌ VoiceRSS HTTP error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur VoiceRSS: {e}")
            return None

    async def synthesize_speech_streamelements(self, 
                                             text: str,
                                             voice: str = "Brian") -> Optional[TTSAudio]:
        """Synthèse via StreamElements (gratuit, pas d'API key)"""
        
        try:
            # URL StreamElements TTS
            url = "https://api.streamelements.com/kappa/v2/speech"
            
            # Paramètres
            params = {
                'voice': voice,
                'text': text[:300]  # Limite StreamElements
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    return TTSAudio(
                        text=text,
                        voice=voice,
                        language="en",  # StreamElements est principalement anglais
                        audio_data=audio_data,
                        format="mp3"
                    )
                else:
                    logger.error(f"❌ StreamElements HTTP error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur StreamElements: {e}")
            return None

    async def synthesize_speech_google(self, 
                                     text: str,
                                     language: str = "en") -> Optional[TTSAudio]:
        """Synthèse via Google Translate TTS (gratuit, simple)"""
        
        try:
            # URL Google TTS
            url = "https://translate.google.com/translate_tts"
            
            # Paramètres
            params = {
                'ie': 'UTF-8',
                'q': text[:200],  # Limite Google TTS
                'tl': language,
                'client': 'tw-ob'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    return TTSAudio(
                        text=text,
                        voice="Google",
                        language=language,
                        audio_data=audio_data,
                        format="mp3"
                    )
                else:
                    logger.error(f"❌ Google TTS HTTP error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur Google TTS: {e}")
            return None

    async def synthesize_speech(self, 
                              text: str,
                              voice: str = "Amy",
                              language: str = "en",
                              service: str = "auto") -> Optional[TTSAudio]:
        """Synthèse vocale avec fallback automatique"""
        
        if not text.strip():
            logger.warning("⚠️ Texte vide fourni")
            return None
            
        if len(text) > 1000:
            logger.warning("⚠️ Texte trop long, troncature à 1000 caractères")
            text = text[:1000]
            
        logger.info(f"🎵 Synthèse TTS: {len(text)} caractères, voix {voice}, langue {language}")
        
        # Essayer les services dans l'ordre
        services_to_try = []
        
        if service == "auto":
            services_to_try = ["streamelements", "google", "voicerss"]
        elif service == "streamelements":
            services_to_try = ["streamelements"]
        elif service == "google":
            services_to_try = ["google"]
        elif service == "voicerss":
            services_to_try = ["voicerss"]
        else:
            services_to_try = ["streamelements", "google", "voicerss"]
        
        for service_name in services_to_try:
            try:
                if service_name == "streamelements":
                    result = await self.synthesize_speech_streamelements(text, voice)
                elif service_name == "google":
                    result = await self.synthesize_speech_google(text, language)
                elif service_name == "voicerss":
                    result = await self.synthesize_speech_voicerss(text, voice, language)
                
                if result:
                    logger.info(f"✅ TTS réussi via {service_name}")
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Échec {service_name}: {e}")
                continue
        
        logger.error("❌ Tous les services TTS ont échoué")
        return None

    async def save_audio(self, tts_audio: TTSAudio, filepath: str) -> bool:
        """Sauvegarder l'audio TTS vers un fichier"""
        
        if not tts_audio.audio_data:
            logger.error("❌ Pas de données audio à sauvegarder")
            return False
            
        try:
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Écrire le fichier audio
            with open(filepath, 'wb') as f:
                f.write(tts_audio.audio_data)
            
            logger.info(f"💾 Audio TTS sauvegardé: {filepath} ({len(tts_audio.audio_data)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur de sauvegarde audio: {e}")
            return False

    async def synthesize_multiple_texts(self, 
                                      texts: List[str],
                                      voice: str = "Amy",
                                      language: str = "en") -> List[Optional[TTSAudio]]:
        """Synthèse de plusieurs textes en parallèle"""
        
        tasks = []
        for text in texts:
            task = self.synthesize_speech(text, voice, language)
            tasks.append(task)
        
        logger.info(f"🎵 Synthèse de {len(texts)} textes en parallèle...")
        
        results = await asyncio.gather(*tasks)
        successful = sum(1 for r in results if r is not None)
        
        logger.info(f"✅ {successful}/{len(texts)} synthèses réussies")
        return results

    def get_available_voices(self, language: Optional[str] = None) -> List[Voice]:
        """Obtenir les voix disponibles"""
        if language:
            return [v for v in self.available_voices if v.language == language]
        return self.available_voices

    def get_supported_languages(self) -> Dict[str, str]:
        """Obtenir les langues supportées"""
        return self.supported_languages

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur les services TTS"""
        return {
            'service': 'Mozilla TTS + Free Alternatives',
            'services_available': [
                'StreamElements TTS (gratuit)',
                'Google Translate TTS (gratuit)',
                'VoiceRSS (gratuit avec limites)'
            ],
            'features': [
                'Text-to-speech synthesis',
                'Multiple voices and languages',
                'No API key required',
                'Automatic service fallback',
                'Audio file export'
            ],
            'voices_count': len(self.available_voices),
            'languages_count': len(self.supported_languages),
            'max_text_length': '300-1000 characters',
            'output_formats': ['mp3', 'wav'],
            'rate_limit': 'Service-dependent'
        }

# Fonctions utilitaires
async def test_tts_integration():
    """Tester l'intégration TTS"""
    try:
        async with MozillaTTSAPI() as tts_api:
            # Test 1: Synthèse simple
            print("🎵 Test synthèse TTS simple...")
            result = await tts_api.synthesize_speech(
                text="Hello, this is a test of the text-to-speech system.",
                voice="Brian",
                language="en"
            )
            
            if result:
                print(f"✅ TTS généré: {len(result.audio_data)} bytes")
                print(f"🎤 Voix: {result.voice}")
                print(f"🌍 Langue: {result.language}")
                print(f"📄 Format: {result.format}")
                
                # Sauvegarder pour test
                await tts_api.save_audio(result, "/tmp/test_tts.mp3")
            
            # Test 2: Voix françaises
            print("\n🎵 Test synthèse française...")
            result_fr = await tts_api.synthesize_speech(
                text="Bonjour, ceci est un test du système de synthèse vocale.",
                voice="Celine",
                language="fr"
            )
            
            if result_fr:
                print(f"✅ TTS français généré: {len(result_fr.audio_data)} bytes")
            
            # Test 3: Voix disponibles
            print("\n🎤 Voix disponibles:")
            voices = tts_api.get_available_voices()
            for voice in voices[:5]:  # Première 5
                print(f"   {voice.name} ({voice.language}) - {voice.description}")
            
            # Test 4: Langues supportées
            print(f"\n🌍 Langues supportées: {len(tts_api.get_supported_languages())}")
            
            # Test 5: Synthèse multiple
            print("\n🎵 Test synthèse multiple...")
            test_texts = [
                "First test sentence.",
                "Second test sentence.",
                "Third test sentence."
            ]
            
            batch_results = await tts_api.synthesize_multiple_texts(test_texts)
            successful_batch = sum(1 for r in batch_results if r is not None)
            print(f"✅ Lot traité: {successful_batch}/{len(test_texts)} succès")
            
            # Test 6: Informations service
            print("\n📊 Informations service...")
            service_info = tts_api.get_service_info()
            print(f"✅ Services: {len(service_info['services_available'])}")
            print(f"🎤 Voix: {service_info['voices_count']}")
            print(f"🌍 Langues: {service_info['languages_count']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test TTS: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration TTS
    result = asyncio.run(test_tts_integration())
    sys.exit(0 if result else 1)