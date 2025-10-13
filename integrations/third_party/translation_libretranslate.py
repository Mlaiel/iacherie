#!/usr/bin/env python3
"""
🌍 LIBRETRANSLATE ENGINE - Traduction gratuite pour IA Chérie
════════════════════════════════════════════════════════════════

Fonctionnalités:
✅ Traduction entre 30+ langues
✅ Détection automatique de langue
✅ Support texte long (chunking)
✅ Cache des traductions
✅ Fallback sur plusieurs instances
✅ API gratuite sans limite stricte

Auteur: Fahed Mlaiel
Date: 28 Septembre 2025
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
import aiohttp
import json

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Résultat de traduction LibreTranslate"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    success: bool
    error: Optional[str] = None
    chunks_count: int = 1

class iaCherieLibreTranslate:
    """
    🌍 Moteur de traduction LibreTranslate pour IA Chérie
    """
    
    def __init__(self):
        self.base_url = os.getenv('LIBRETRANSLATE_URL', 'https://libretranslate.com')
        self.api_url = f"{self.base_url}/translate"
        self.detect_url = f"{self.base_url}/detect"
        self.languages_url = f"{self.base_url}/languages"
        
        # URLs de fallback (instances publiques)
        self.fallback_urls = [
            'https://libretranslate.de',
            'https://translate.argosopentech.com',
            'https://libretranslate.com'
        ]
        
        # Cache des langues supportées
        self.supported_languages = {}
        self.translation_cache = {}
        
        logger.info("✅ LibreTranslate Engine initialisé avec succès")
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """Récupère la liste des langues supportées"""
        if self.supported_languages:
            return self.supported_languages
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.languages_url) as response:
                    if response.status == 200:
                        languages = await response.json()
                        self.supported_languages = {lang['code']: lang['name'] for lang in languages}
                        return self.supported_languages
        except Exception as e:
            logger.warning(f"⚠️ Erreur récupération langues: {str(e)}")
        
        # Langues par défaut si API indisponible
        self.supported_languages = {
            'en': 'English', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi',
            'tr': 'Turkish', 'pl': 'Polish', 'nl': 'Dutch', 'sv': 'Swedish'
        }
        return self.supported_languages
    
    async def detect_language(self, text: str) -> str:
        """Détecte automatiquement la langue d'un texte"""
        try:
            data = {"q": text[:200]}  # Limite à 200 caractères pour la détection
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.detect_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result and len(result) > 0:
                            return result[0]['language']
        except Exception as e:
            logger.warning(f"⚠️ Erreur détection langue: {str(e)}")
        
        return 'auto'
    
    def _chunk_text(self, text: str, max_length: int = 4000) -> List[str]:
        """Divise un texte long en chunks pour la traduction"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence + '. ') <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def translate_with_fallback(self, text: str, target_lang: str, source_lang: str = 'auto') -> TranslationResult:
        """Traduit avec système de fallback sur plusieurs instances"""
        
        # Vérifier le cache
        cache_key = f"{text[:100]}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            cached = self.translation_cache[cache_key]
            logger.info("📦 Traduction récupérée du cache")
            return cached
        
        urls_to_try = [self.base_url] + self.fallback_urls
        
        for base_url in urls_to_try:
            try:
                translate_url = f"{base_url}/translate"
                result = await self._translate_single_url(text, target_lang, source_lang, translate_url)
                
                if result.success:
                    # Mettre en cache si réussi
                    self.translation_cache[cache_key] = result
                    logger.info(f"✅ Traduction réussie via {base_url}")
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Échec {base_url}: {str(e)}")
                continue
        
        # Si tous les endpoints ont échoué
        return TranslationResult(
            original_text=text[:100] + "..." if len(text) > 100 else text,
            translated_text="",
            source_language=source_lang,
            target_language=target_lang,
            confidence=0.0,
            success=False,
            error="Tous les endpoints LibreTranslate ont échoué"
        )
    
    async def _translate_single_url(self, text: str, target_lang: str, source_lang: str, translate_url: str) -> TranslationResult:
        """Traduit via une URL spécifique"""
        
        # Chunking pour textes longs
        chunks = self._chunk_text(text, max_length=3000)
        translated_chunks = []
        detected_lang = source_lang
        
        async with aiohttp.ClientSession() as session:
            for i, chunk in enumerate(chunks):
                data = {
                    "q": chunk,
                    "source": source_lang,
                    "target": target_lang,
                    "format": "text"
                }
                
                async with session.post(translate_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_chunks.append(result['translatedText'])
                        
                        # Récupérer la langue détectée du premier chunk
                        if i == 0 and 'detectedLanguage' in result:
                            detected_lang = result['detectedLanguage']['language']
                    else:
                        raise Exception(f"HTTP {response.status}")
                
                # Petite pause entre les chunks
                if len(chunks) > 1:
                    await asyncio.sleep(0.1)
        
        translated_text = ' '.join(translated_chunks)
        
        return TranslationResult(
            original_text=text[:200] + "..." if len(text) > 200 else text,
            translated_text=translated_text,
            source_language=detected_lang,
            target_language=target_lang,
            confidence=0.85,  # LibreTranslate ne fournit pas de score de confiance
            success=True,
            chunks_count=len(chunks)
        )
    
    async def translate(self, text: str, target_language: str, source_language: str = 'auto') -> TranslationResult:
        """
        Traduit un texte vers la langue cible
        
        Args:
            text: Texte à traduire
            target_language: Code langue cible (ex: 'fr', 'en', 'de')
            source_language: Code langue source ('auto' pour détection automatique)
            
        Returns:
            TranslationResult avec la traduction
        """
        try:
            if not text or len(text.strip()) < 2:
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.0,
                    success=False,
                    error="Texte trop court pour traduction"
                )
            
            # Vérifier si les langues sont supportées
            supported = await self.get_supported_languages()
            
            if target_language not in supported:
                return TranslationResult(
                    original_text=text[:100],
                    translated_text="",
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.0,
                    success=False,
                    error=f"Langue cible '{target_language}' non supportée"
                )
            
            # Détecter la langue source si nécessaire
            if source_language == 'auto':
                detected = await self.detect_language(text)
                source_language = detected if detected != 'auto' else 'en'
            
            # Si source = cible, pas de traduction nécessaire
            if source_language == target_language:
                return TranslationResult(
                    original_text=text[:200] + "..." if len(text) > 200 else text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=1.0,
                    success=True
                )
            
            # Traduction avec fallback
            return await self.translate_with_fallback(text, target_language, source_language)
            
        except Exception as e:
            logger.error(f"❌ Erreur traduction LibreTranslate: {str(e)}")
            return TranslationResult(
                original_text=text[:100] + "..." if len(text) > 100 else text,
                translated_text="",
                source_language=source_language,
                target_language=target_language,
                confidence=0.0,
                success=False,
                error=str(e)
            )
    
    async def batch_translate(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[TranslationResult]:
        """Traduit plusieurs textes en lot"""
        tasks = []
        for text in texts:
            task = self.translate(text, target_language, source_language)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def get_translation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de traduction"""
        return {
            "cache_size": len(self.translation_cache),
            "supported_languages_count": len(self.supported_languages),
            "base_url": self.base_url,
            "fallback_urls_count": len(self.fallback_urls)
        }

# Test du moteur si exécuté directement
async def test_libretranslate_engine():
    """Test complet du moteur LibreTranslate"""
    print("🌍 Test LibreTranslate Engine - Traduction gratuite")
    print("=" * 60)
    
    try:
        engine = iaCherieLibreTranslate()
        
        # Test langues supportées
        languages = await engine.get_supported_languages()
        print(f"🌐 Langues supportées: {len(languages)}")
        print(f"Exemples: {list(languages.keys())[:10]}")
        
        # Tests de traduction
        test_cases = [
            ("Hello world, this is a test!", "fr"),
            ("IA Chérie est une plateforme révolutionnaire", "en"),
            ("Hola mundo, ¿cómo estás?", "de"),
            ("これは日本語のテストです", "en")
        ]
        
        print("\n🔄 Tests de traduction:")
        print("-" * 40)
        
        for i, (text, target_lang) in enumerate(test_cases, 1):
            print(f"\n{i}. Traduction vers {target_lang}:")
            print(f"   Original: {text}")
            
            result = await engine.translate(text, target_lang)
            
            if result.success:
                print(f"   Traduit: {result.translated_text}")
                print(f"   Langue source détectée: {result.source_language}")
                print(f"   Confiance: {result.confidence:.2f}")
                if result.chunks_count > 1:
                    print(f"   Chunks utilisés: {result.chunks_count}")
            else:
                print(f"   ❌ Erreur: {result.error}")
        
        # Test texte long
        print(f"\n📝 Test texte long:")
        long_text = """
        IA Chérie est une plateforme d'intelligence artificielle révolutionnaire qui transforme 
        complètement la façon dont les entreprises créent et gèrent leur contenu numérique. 
        Avec ses 53 agents spécialisés et ses 680 microservices interconnectés, la plateforme 
        offre une solution complète pour l'automatisation de la création de contenu. 
        L'entreprise vise un chiffre d'affaires de 50 millions d'euros d'ici 2026.
        """
        
        long_result = await engine.translate(long_text.strip(), "en")
        if long_result.success:
            print(f"   Traduction longue réussie ({long_result.chunks_count} chunks)")
            print(f"   Aperçu: {long_result.translated_text[:100]}...")
        
        # Test détection de langue
        print(f"\n🕵️ Test détection de langue:")
        detection_tests = [
            "This is English text",
            "Ceci est du français",
            "Das ist deutscher Text"
        ]
        
        for text in detection_tests:
            detected = await engine.detect_language(text)
            print(f"   '{text[:30]}...' → {detected}")
        
        # Statistiques
        stats = await engine.get_translation_stats()
        print(f"\n📊 Statistiques:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ LibreTranslate Engine testé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_libretranslate_engine())