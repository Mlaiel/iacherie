#!/usr/bin/env python3
"""
🌍 LIBRETRANSLATE API INTEGRATION
Service de traduction gratuit et open source
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Résultat d'une traduction"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: Optional[float] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class LanguageInfo:
    """Information sur une langue"""
    code: str
    name: str
    targets: List[str] = None

class LibreTranslateAPI:
    """Client API pour LibreTranslate - Service gratuit de traduction"""
    
    def __init__(self, base_url: str = "https://libretranslate.com"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.available_languages = {}
        
        # Headers par défaut
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'IA Chérie-Platform/1.0'
        }
        
        logger.info(f"🌍 LibreTranslateAPI initialisé - URL: {self.base_url}")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Charger les langues disponibles
        await self._load_languages()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def _load_languages(self) -> None:
        """Charger la liste des langues disponibles"""
        try:
            url = f"{self.base_url}/languages"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    languages = await response.json()
                    
                    for lang in languages:
                        self.available_languages[lang['code']] = LanguageInfo(
                            code=lang['code'],
                            name=lang['name'],
                            targets=lang.get('targets', [])
                        )
                    
                    logger.info(f"✅ {len(self.available_languages)} langues chargées")
                else:
                    logger.warning(f"⚠️ Impossible de charger les langues: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur de chargement des langues: {e}")

    async def translate(self, 
                       text: str,
                       target_language: str,
                       source_language: str = "auto") -> Optional[TranslationResult]:
        """Traduire un texte"""
        
        if not text.strip():
            logger.warning("⚠️ Texte vide fourni")
            return None
            
        # Vérifier si la langue cible est disponible
        if target_language not in self.available_languages:
            logger.error(f"❌ Langue cible non supportée: {target_language}")
            return None
            
        logger.info(f"🌍 Traduction: {source_language} → {target_language}")
        logger.info(f"📝 Texte: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        try:
            url = f"{self.base_url}/translate"
            
            payload = {
                "q": text,
                "source": source_language,
                "target": target_language,
                "format": "text"
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    translated_text = data.get('translatedText', '')
                    
                    # Détecter la langue source si auto
                    detected_source = data.get('detectedLanguage', {}).get('language', source_language)
                    confidence = data.get('detectedLanguage', {}).get('confidence')
                    
                    result = TranslationResult(
                        original_text=text,
                        translated_text=translated_text,
                        source_language=detected_source,
                        target_language=target_language,
                        confidence=confidence
                    )
                    
                    logger.info(f"✅ Traduction réussie: {len(translated_text)} caractères")
                    return result
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    error_data = await response.text()
                    logger.error(f"❌ Erreur de traduction: {response.status} - {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de traduction: {e}")
            return None

    async def detect_language(self, text: str) -> Optional[Dict[str, Any]]:
        """Détecter la langue d'un texte"""
        
        if not text.strip():
            return None
            
        try:
            url = f"{self.base_url}/detect"
            
            payload = {"q": text}
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    detection = {
                        'language': data.get('language'),
                        'confidence': data.get('confidence'),
                        'language_name': self.available_languages.get(
                            data.get('language'), 
                            LanguageInfo('unknown', 'Unknown')
                        ).name
                    }
                    
                    logger.info(f"✅ Langue détectée: {detection['language_name']} ({detection['confidence']:.2f})")
                    return detection
                else:
                    logger.error(f"❌ Erreur de détection: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de détection: {e}")
            return None

    async def translate_multiple(self, 
                               texts: List[str],
                               target_language: str,
                               source_language: str = "auto") -> List[Optional[TranslationResult]]:
        """Traduire plusieurs textes en parallèle"""
        
        tasks = []
        for text in texts:
            task = self.translate(text, target_language, source_language)
            tasks.append(task)
        
        logger.info(f"🌍 Traduction de {len(texts)} textes en parallèle...")
        
        results = await asyncio.gather(*tasks)
        successful = sum(1 for r in results if r is not None)
        
        logger.info(f"✅ {successful}/{len(texts)} traductions réussies")
        return results

    async def translate_to_multiple_languages(self, 
                                            text: str,
                                            target_languages: List[str],
                                            source_language: str = "auto") -> Dict[str, Optional[TranslationResult]]:
        """Traduire un texte vers plusieurs langues"""
        
        tasks = {}
        for lang in target_languages:
            tasks[lang] = self.translate(text, lang, source_language)
        
        logger.info(f"🌍 Traduction vers {len(target_languages)} langues...")
        
        results = {}
        for lang, task in tasks.items():
            results[lang] = await task
        
        successful = sum(1 for r in results.values() if r is not None)
        logger.info(f"✅ {successful}/{len(target_languages)} traductions réussies")
        
        return results

    def get_supported_languages(self) -> Dict[str, LanguageInfo]:
        """Obtenir la liste des langues supportées"""
        return self.available_languages.copy()

    def get_language_name(self, language_code: str) -> str:
        """Obtenir le nom d'une langue par son code"""
        return self.available_languages.get(language_code, LanguageInfo('unknown', 'Unknown')).name

    def is_language_supported(self, language_code: str) -> bool:
        """Vérifier si une langue est supportée"""
        return language_code in self.available_languages

    async def get_service_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le service"""
        try:
            # Test de base pour vérifier la disponibilité
            test_result = await self.translate("Hello", "fr", "en")
            
            return {
                'service': 'LibreTranslate',
                'base_url': self.base_url,
                'available': test_result is not None,
                'languages_count': len(self.available_languages),
                'rate_limit': '20 requests per minute (free tier)',
                'features': [
                    'Text translation',
                    'Language detection',
                    'Multiple languages support',
                    'Open source',
                    'No API key required'
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur d'info service: {e}")
            return {'service': 'LibreTranslate', 'available': False, 'error': str(e)}

# Langues les plus courantes pour faciliter l'utilisation
COMMON_LANGUAGES = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'pl': 'Polish',
    'tr': 'Turkish'
}

# Fonctions utilitaires
async def test_integration():
    """Tester l'intégration LibreTranslate"""
    try:
        async with LibreTranslateAPI() as api:
            # Test 1: Traduction simple
            print("🌍 Test traduction simple...")
            result = await api.translate(
                text="Hello, how are you today?",
                target_language="fr",
                source_language="en"
            )
            
            if result:
                print(f"✅ Traduction réussie:")
                print(f"   📝 Original ({result.source_language}): {result.original_text}")
                print(f"   🌍 Traduit ({result.target_language}): {result.translated_text}")
            
            # Test 2: Détection de langue
            print("\n🔍 Test détection de langue...")
            detection = await api.detect_language("Bonjour, comment allez-vous?")
            
            if detection:
                print(f"✅ Langue détectée: {detection['language_name']} ({detection['confidence']:.2f})")
            
            # Test 3: Traduction multiple
            print("\n🌐 Test traduction vers multiples langues...")
            multi_results = await api.translate_to_multiple_languages(
                text="Welcome to our platform!",
                target_languages=["fr", "es", "de"],
                source_language="en"
            )
            
            for lang, trans_result in multi_results.items():
                if trans_result:
                    lang_name = api.get_language_name(lang)
                    print(f"   🌍 {lang_name}: {trans_result.translated_text}")
            
            # Test 4: Informations sur le service
            print("\n📊 Informations sur le service...")
            service_info = await api.get_service_info()
            
            print(f"✅ Service: {service_info['service']}")
            print(f"🌍 Langues supportées: {service_info.get('languages_count', 'N/A')}")
            print(f"⚡ Disponible: {service_info.get('available', False)}")
            
            # Afficher quelques langues supportées
            print("\n🗣️ Langues supportées (échantillon):")
            languages = api.get_supported_languages()
            for code, info in list(languages.items())[:10]:
                print(f"   {code}: {info.name}")
            
            return service_info.get('available', False)
            
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)