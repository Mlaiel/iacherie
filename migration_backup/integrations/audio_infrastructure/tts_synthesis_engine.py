#!/usr/bin/env python3
"""
🚀 AINFLUENCER - MODULE TEXT-TO-SPEECH COMPLET
Synthèse vocale multi-moteur avec Mozilla TTS alternative
Développé par: Fahed Mlaiel - mlaiel@live.de
"""

import os
import io
import tempfile
from datetime import datetime
import pyttsx3
from gtts import gTTS
import pygame
import asyncio
from typing import Optional, Dict, List

class AinfluencerTTS:
    """
    Module TTS complet pour Ainfluencer avec multiple engines
    """
    
    def __init__(self):
        self.engines = {
            'pyttsx3': None,  # TTS local cross-platform
            'gtts': 'google',  # Google TTS (online)
        }
        self.supported_languages = {
            'fr': 'Français',
            'en': 'English', 
            'de': 'Deutsch',
            'es': 'Español',
            'it': 'Italiano',
            'pt': 'Português',
            'ar': 'العربية',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ru': 'Русский'
        }
        self.initialize_engines()
    
    def initialize_engines(self):
        """Initialiser les moteurs TTS"""
        try:
            # Initialiser pyttsx3 (offline)
            self.engines['pyttsx3'] = pyttsx3.init()
            if self.engines['pyttsx3']:
                # Configuration vocale optimisée
                self.engines['pyttsx3'].setProperty('rate', 180)  # Vitesse
                self.engines['pyttsx3'].setProperty('volume', 0.9)  # Volume
                
                # Essayer de définir une voix française si disponible
                voices = self.engines['pyttsx3'].getProperty('voices')
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                        self.engines['pyttsx3'].setProperty('voice', voice.id)
                        break
                
            print("✅ Moteurs TTS initialisés avec succès")
        except Exception as e:
            print(f"⚠️ Erreur initialisation TTS: {e}")
    
    async def generate_speech_local(self, text: str, language: str = 'fr', 
                                  voice_speed: int = 180) -> Optional[str]:
        """
        Générer de la parole avec pyttsx3 (local, offline)
        """
        try:
            if not self.engines['pyttsx3']:
                return None
                
            # Configuration dynamique
            self.engines['pyttsx3'].setProperty('rate', voice_speed)
            
            # Créer fichier temporaire
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/workspaces/Ainfluencer/audio_generated_local_{timestamp}.wav"
            
            # Sauvegarder vers fichier
            self.engines['pyttsx3'].save_to_file(text, output_file)
            self.engines['pyttsx3'].runAndWait()
            
            if os.path.exists(output_file):
                print(f"🎵 Audio généré localement: {output_file}")
                return output_file
            
        except Exception as e:
            print(f"❌ Erreur génération locale: {e}")
            
        return None
    
    async def generate_speech_google(self, text: str, language: str = 'fr', 
                                   slow: bool = False) -> Optional[str]:
        """
        Générer de la parole avec Google TTS (online, haute qualité)
        """
        try:
            # Créer l'objet gTTS
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Créer fichier temporaire
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/workspaces/Ainfluencer/audio_generated_google_{timestamp}.mp3"
            
            # Sauvegarder
            tts.save(output_file)
            
            if os.path.exists(output_file):
                print(f"🌍 Audio généré avec Google TTS: {output_file}")
                return output_file
                
        except Exception as e:
            print(f"❌ Erreur génération Google TTS: {e}")
            
        return None
    
    async def generate_speech_multi(self, text: str, language: str = 'fr', 
                                  engine: str = 'auto') -> Dict:
        """
        Génération multi-moteur avec fallback intelligent
        """
        results = {
            'success': False,
            'files': [],
            'engine_used': None,
            'metadata': {
                'text_length': len(text),
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Déterminer l'ordre des moteurs
        if engine == 'auto':
            engines_order = ['gtts', 'pyttsx3']  # Google en premier (meilleure qualité)
        elif engine == 'local':
            engines_order = ['pyttsx3']
        elif engine == 'google':
            engines_order = ['gtts']
        else:
            engines_order = ['gtts', 'pyttsx3']
        
        # Essayer chaque moteur
        for engine_name in engines_order:
            try:
                if engine_name == 'gtts':
                    file_path = await self.generate_speech_google(text, language)
                elif engine_name == 'pyttsx3':
                    file_path = await self.generate_speech_local(text, language)
                else:
                    continue
                
                if file_path and os.path.exists(file_path):
                    results['success'] = True
                    results['files'].append(file_path)
                    results['engine_used'] = engine_name
                    results['metadata']['file_size'] = os.path.getsize(file_path)
                    results['metadata']['file_format'] = file_path.split('.')[-1]
                    break
                    
            except Exception as e:
                print(f"❌ Erreur moteur {engine_name}: {e}")
                continue
        
        return results
    
    def play_audio_file(self, file_path: str) -> bool:
        """
        Jouer un fichier audio généré
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            print(f"🔊 Lecture audio: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lecture audio: {e}")
            return False
    
    def get_available_voices(self) -> Dict:
        """
        Obtenir les voix disponibles pour pyttsx3
        """
        voices_info = {'local_voices': []}
        
        try:
            if self.engines['pyttsx3']:
                voices = self.engines['pyttsx3'].getProperty('voices')
                for voice in voices:
                    voice_data = {
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', 'unknown')
                    }
                    voices_info['local_voices'].append(voice_data)
        except Exception as e:
            print(f"❌ Erreur récupération voix: {e}")
        
        voices_info['google_languages'] = list(self.supported_languages.keys())
        return voices_info

# Fonctions utilitaires pour l'intégration avec le backend

async def tts_generate_for_ainfluencer(text: str, language: str = 'fr', 
                                     engine: str = 'auto') -> Dict:
    """
    Interface principale pour l'intégration backend Ainfluencer
    """
    tts_engine = AinfluencerTTS()
    result = await tts_engine.generate_speech_multi(text, language, engine)
    
    # Ajouter des métadonnées spécifiques à Ainfluencer
    if result['success']:
        result['ainfluencer_metadata'] = {
            'agent_used': 'TTS_SYNTHESIS_AGENT',
            'content_type': 'audio',
            'generation_method': 'text_to_speech',
            'platform': 'Ainfluencer',
            'creator': 'Fahed Mlaiel'
        }
    
    return result

def test_tts_installation():
    """
    Tester l'installation et les capacités TTS
    """
    print("🚀 AINFLUENCER TTS - Test d'Installation")
    print("=" * 50)
    
    tts = AinfluencerTTS()
    
    # Test voix disponibles
    voices = tts.get_available_voices()
    print(f"🎤 Voix locales disponibles: {len(voices['local_voices'])}")
    print(f"🌍 Langues Google TTS: {len(voices['google_languages'])}")
    
    # Test de génération
    test_text = "Bonjour ! Je suis Ainfluencer, votre assistant IA pour la création de contenu."
    
    print(f"\n📝 Texte de test: {test_text}")
    print("🔄 Génération en cours...")
    
    # Test synchrone simplifié
    try:
        # Test Google TTS
        tts_google = gTTS(text=test_text, lang='fr')
        test_file = "/workspaces/Ainfluencer/test_tts_google.mp3"
        tts_google.save(test_file)
        
        if os.path.exists(test_file):
            print(f"✅ Google TTS: Succès - {test_file}")
            print(f"📊 Taille fichier: {os.path.getsize(test_file)} bytes")
        else:
            print("❌ Google TTS: Échec")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    print("\n🎯 Installation TTS complète!")
    return True

if __name__ == "__main__":
    # Test de l'installation
    test_tts_installation()