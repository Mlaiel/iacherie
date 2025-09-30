#!/usr/bin/env python3
"""
🎯 FREE APIS UNIFIED INTEGRATION
Intégration unifiée de tous les services d'APIs gratuites
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Imports des APIs gratuites
try:
    from pollinations_ai_api import PollinationsAPI, GeneratedImage
    from libretranslate_api import LibreTranslateAPI, TranslationResult
    from url_services_api import URLServicesIntegration, QRCode, ShortURL, TinyURLAPI
    from mozilla_tts_api import MozillaTTSAPI, TTSAudio
    from google_fonts_api import GoogleFontsAPI, FontFamily
    from coingecko_api import CoinGeckoAPI, CoinData
    from pagespeed_alternative import AlternativePageSpeedAPI, AlternativePageSpeedResult
except ImportError:
    # Fallback pour exécution directe
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from pollinations_ai_api import PollinationsAPI, GeneratedImage
    from libretranslate_api import LibreTranslateAPI, TranslationResult
    from url_services_api import URLServicesIntegration, QRCode, ShortURL, TinyURLAPI
    from mozilla_tts_api import MozillaTTSAPI, TTSAudio
    from google_fonts_api import GoogleFontsAPI, FontFamily
    from coingecko_api import CoinGeckoAPI, CoinData
    from pagespeed_alternative import AlternativePageSpeedAPI, AlternativePageSpeedResult

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FreeAPIService:
    """Informations sur un service API gratuit"""
    name: str
    category: str
    status: str  # "active", "limited", "unavailable"
    features: List[str]
    rate_limit: str
    requires_key: bool
    description: str

class FreeAPIsManager:
    """Gestionnaire unifié de tous les services d'APIs gratuites"""
    
    def __init__(self, tinyurl_api_key: Optional[str] = None):
        self.services = {}
        self.initialized = False
        self.tinyurl_api_key = tinyurl_api_key or "V6nENR9gI5ESnWfKRORk715xHV2kywjjvAPkry5OhlDamik7hM5X1FMfjB7u"
        
        # Services disponibles
        self.available_services = {
            "pollinations": {
                "name": "Pollinations AI",
                "category": "AI/Image Generation",
                "class": PollinationsAPI,
                "requires_key": False,
                "description": "Génération d'images IA gratuite et illimitée"
            },
            "libretranslate": {
                "name": "LibreTranslate",
                "category": "Translation",
                "class": LibreTranslateAPI,
                "requires_key": False,
                "description": "Service de traduction gratuit et open source"
            },
            "url_services": {
                "name": "URL Services (QR + Short URLs)",
                "category": "Utilities",
                "class": URLServicesIntegration,
                "requires_key": False,
                "description": "QR codes et raccourcissement d'URLs gratuits"
            },
            "mozilla_tts": {
                "name": "Mozilla TTS",
                "category": "AI/Speech",
                "class": MozillaTTSAPI,
                "requires_key": False,
                "description": "Synthèse vocale gratuite multi-langues"
            },
            "google_fonts": {
                "name": "Google Fonts",
                "category": "Design/Fonts",
                "class": GoogleFontsAPI,
                "requires_key": False,
                "description": "Accès gratuit à la bibliothèque Google Fonts"
            },
            "coingecko": {
                "name": "CoinGecko",
                "category": "Finance/Crypto",
                "class": CoinGeckoAPI,
                "requires_key": False,
                "description": "Données crypto-monnaies gratuites"
            },
            "pagespeed": {
                "name": "PageSpeed Alternative",
                "category": "Performance/Analytics",
                "class": AlternativePageSpeedAPI,
                "requires_key": False,
                "description": "Analyse de performance web gratuite"
            }
        }
        
        logger.info("🎯 FreeAPIsManager initialisé avec 7 services gratuits")

    async def __aenter__(self):
        """Initialiser tous les services"""
        await self.initialize_all_services()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer tous les services"""
        await self.cleanup_all_services()

    async def initialize_all_services(self):
        """Initialiser tous les services disponibles"""
        
        logger.info("🎯 Initialisation de tous les services gratuits...")
        
        initialization_results = {}
        
        for service_id, service_config in self.available_services.items():
            try:
                # Créer l'instance du service
                service_class = service_config["class"]
                
                # Configuration spéciale pour URL Services avec clé TinyURL
                if service_id == "url_services":
                    service_instance = service_class()
                    # Injecter la clé TinyURL après création
                    service_instance.tiny_api = TinyURLAPI(api_key=self.tinyurl_api_key)
                else:
                    service_instance = service_class()
                
                # Initialiser le service (entrer dans le context manager)
                await service_instance.__aenter__()
                
                # Stocker le service
                self.services[service_id] = service_instance
                initialization_results[service_id] = "✅ Initialisé"
                
                logger.info(f"✅ {service_config['name']} initialisé")
                
            except Exception as e:
                initialization_results[service_id] = f"❌ Erreur: {e}"
                logger.error(f"❌ Erreur initialisation {service_config['name']}: {e}")
        
        self.initialized = True
        
        # Rapport d'initialisation
        successful = sum(1 for status in initialization_results.values() if status.startswith("✅"))
        total = len(self.available_services)
        
        logger.info(f"🎯 Initialisation terminée: {successful}/{total} services actifs")
        
        return initialization_results

    async def cleanup_all_services(self):
        """Nettoyer tous les services"""
        
        logger.info("🎯 Nettoyage de tous les services...")
        
        for service_id, service_instance in self.services.items():
            try:
                await service_instance.__aexit__(None, None, None)
                logger.info(f"✅ {service_id} nettoyé")
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage {service_id}: {e}")
        
        self.services.clear()
        self.initialized = False

    # === SERVICES D'IA ===
    
    async def generate_ai_image(self, 
                              prompt: str,
                              model: str = "flux",
                              width: int = 1024,
                              height: int = 1024,
                              enhance: bool = True) -> Optional[GeneratedImage]:
        """Générer une image IA via Pollinations"""
        
        if "pollinations" not in self.services:
            logger.error("❌ Service Pollinations non disponible")
            return None
            
        return await self.services["pollinations"].generate_image(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            enhance=enhance
        )

    async def translate_text(self, 
                           text: str,
                           target_language: str,
                           source_language: str = "auto") -> Optional[TranslationResult]:
        """Traduire du texte via LibreTranslate"""
        
        if "libretranslate" not in self.services:
            logger.error("❌ Service LibreTranslate non disponible")
            return None
            
        return await self.services["libretranslate"].translate(
            text=text,
            target_language=target_language,
            source_language=source_language
        )

    async def synthesize_speech(self, 
                              text: str,
                              voice: str = "Amy",
                              language: str = "en") -> Optional[TTSAudio]:
        """Synthèse vocale via Mozilla TTS"""
        
        if "mozilla_tts" not in self.services:
            logger.error("❌ Service Mozilla TTS non disponible")
            return None
            
        return await self.services["mozilla_tts"].synthesize_speech(
            text=text,
            voice=voice,
            language=language
        )

    # === SERVICES UTILITAIRES ===
    
    async def create_qr_code(self, 
                           data: str,
                           size: str = "300x300") -> Optional[QRCode]:
        """Créer un QR code"""
        
        if "url_services" not in self.services:
            logger.error("❌ Service URL non disponible")
            return None
            
        return await self.services["url_services"].qr_api.generate_qr_code(
            data=data,
            size=size
        )

    async def shorten_url(self, url: str) -> Optional[ShortURL]:
        """Raccourcir une URL"""
        
        if "url_services" not in self.services:
            logger.error("❌ Service URL non disponible")
            return None
            
        return await self.services["url_services"].tiny_api.shorten_url(url)

    async def create_url_with_qr(self, url: str) -> Optional[Dict[str, Any]]:
        """Créer URL raccourcie + QR code"""
        
        if "url_services" not in self.services:
            logger.error("❌ Service URL non disponible")
            return None
            
        return await self.services["url_services"].create_short_url_with_qr(url)

    # === SERVICES DE DESIGN ===
    
    async def search_fonts(self, 
                         query: str,
                         limit: int = 20) -> Optional[List[FontFamily]]:
        """Rechercher des polices Google"""
        
        if "google_fonts" not in self.services:
            logger.error("❌ Service Google Fonts non disponible")
            return None
            
        return await self.services["google_fonts"].search_fonts(
            query=query,
            limit=limit
        )

    async def get_popular_fonts(self, limit: int = 50) -> Optional[List[FontFamily]]:
        """Obtenir les polices populaires"""
        
        if "google_fonts" not in self.services:
            logger.error("❌ Service Google Fonts non disponible")
            return None
            
        return await self.services["google_fonts"].get_popular_fonts(limit)

    # === SERVICES FINANCIERS ===
    
    async def get_crypto_market_data(self, 
                                   per_page: int = 50) -> Optional[List[CoinData]]:
        """Obtenir les données du marché crypto"""
        
        if "coingecko" not in self.services:
            logger.error("❌ Service CoinGecko non disponible")
            return None
            
        return await self.services["coingecko"].get_market_data(per_page=per_page)

    async def get_crypto_data(self, coin_id: str) -> Optional[CoinData]:
        """Obtenir les données d'une crypto spécifique"""
        
        if "coingecko" not in self.services:
            logger.error("❌ Service CoinGecko non disponible")
            return None
            
        return await self.services["coingecko"].get_coin_data(coin_id)

    async def search_crypto(self, query: str) -> Optional[Dict[str, Any]]:
        """Rechercher des crypto-monnaies"""
        
        if "coingecko" not in self.services:
            logger.error("❌ Service CoinGecko non disponible")
            return None
            
        return await self.services["coingecko"].search_coins(query)

    async def analyze_website_performance(self, url: str) -> Optional[AlternativePageSpeedResult]:
        """Analyser la performance d'un site web"""
        
        if "pagespeed" not in self.services:
            logger.error("❌ Service PageSpeed non disponible")
            return None
            
        return await self.services["pagespeed"].analyze_basic_performance(url)

    async def compare_websites_performance(self, urls: List[str]) -> Dict[str, AlternativePageSpeedResult]:
        """Comparer la performance de plusieurs sites"""
        
        if "pagespeed" not in self.services:
            logger.error("❌ Service PageSpeed non disponible")
            return {}
            
        return await self.services["pagespeed"].analyze_multiple_pages(urls)

    # === SERVICES COMBINÉS ===
    
    async def create_multilingual_content(self, 
                                        text: str,
                                        languages: List[str],
                                        generate_speech: bool = False) -> Dict[str, Any]:
        """Créer du contenu multilingue (traduction + TTS optionnel)"""
        
        results = {
            "original_text": text,
            "translations": {},
            "speech_files": {} if generate_speech else None
        }
        
        # Traduire dans toutes les langues
        for lang in languages:
            translation = await self.translate_text(text, lang)
            if translation:
                results["translations"][lang] = translation.translated_text
                
                # Générer le speech si demandé
                if generate_speech:
                    speech = await self.synthesize_speech(
                        text=translation.translated_text,
                        language=lang
                    )
                    if speech:
                        results["speech_files"][lang] = speech
        
        return results

    async def create_branded_content_package(self, 
                                           text: str,
                                           url: str,
                                           image_prompt: str) -> Dict[str, Any]:
        """Créer un package de contenu brandé complet"""
        
        package = {
            "text": text,
            "url": url,
            "image_prompt": image_prompt,
            "generated_image": None,
            "short_url": None,
            "qr_code": None,
            "combined_url_qr": None
        }
        
        # Générer l'image IA
        image = await self.generate_ai_image(image_prompt)
        if image:
            package["generated_image"] = image
        
        # Créer URL courte + QR
        url_qr_combo = await self.create_url_with_qr(url)
        if url_qr_combo and url_qr_combo.get("success"):
            package["short_url"] = url_qr_combo["short_url"]
            package["qr_code"] = url_qr_combo["qr_code"]
            package["combined_url_qr"] = url_qr_combo
        
        return package

    # === INFORMATIONS ET STATUTS ===
    
    def get_services_status(self) -> Dict[str, FreeAPIService]:
        """Obtenir le statut de tous les services"""
        
        status = {}
        
        for service_id, service_config in self.available_services.items():
            is_active = service_id in self.services
            
            # Obtenir les infos du service si actif
            if is_active:
                try:
                    service_info = self.services[service_id].get_service_info()
                    features = service_info.get("features", [])
                    rate_limit = service_info.get("rate_limit", "Unknown")
                except:
                    features = ["Service actif"]
                    rate_limit = "Unknown"
            else:
                features = ["Service non initialisé"]
                rate_limit = "N/A"
            
            status[service_id] = FreeAPIService(
                name=service_config["name"],
                category=service_config["category"],
                status="active" if is_active else "unavailable",
                features=features,
                rate_limit=rate_limit,
                requires_key=service_config["requires_key"],
                description=service_config["description"]
            )
        
        return status

    def get_available_categories(self) -> Dict[str, List[str]]:
        """Obtenir les services par catégorie"""
        
        categories = {}
        
        for service_id, service_config in self.available_services.items():
            category = service_config["category"]
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(service_config["name"])
        
        return categories

    def get_free_apis_summary(self) -> Dict[str, Any]:
        """Résumé complet des APIs gratuites"""
        
        return {
            "total_services": len(self.available_services),
            "active_services": len(self.services),
            "initialization_status": self.initialized,
            "services_by_category": self.get_available_categories(),
            "no_key_required": sum(1 for s in self.available_services.values() if not s["requires_key"]),
            "features_count": {
                "ai_generation": 2,  # Pollinations + TTS
                "translation": 1,    # LibreTranslate
                "utilities": 1,      # URL services
                "design": 1,         # Google Fonts
                "finance": 1,        # CoinGecko
                "performance": 1     # PageSpeed Alternative
            }
        }

# Fonctions utilitaires globales
async def test_all_free_apis():
    """Test complet de toutes les APIs gratuites"""
    
    try:
        async with FreeAPIsManager() as manager:
            print("🎯 === TEST COMPLET DES APIS GRATUITES ===\n")
            
            # Test 1: Statut des services
            print("📊 Statut des services:")
            status = manager.get_services_status()
            for service_id, service_info in status.items():
                print(f"   {service_info.name}: {service_info.status}")
            
            # Test 2: Génération d'image IA
            print("\n🎨 Test génération image IA...")
            image = await manager.generate_ai_image(
                prompt="A beautiful sunset over mountains",
                model="flux"
            )
            if image:
                print(f"✅ Image générée: {image.url}")
            
            # Test 3: Traduction
            print("\n🌍 Test traduction...")
            translation = await manager.translate_text(
                text="Hello, how are you today?",
                target_language="fr"
            )
            if translation:
                print(f"✅ Traduction: {translation.translated_text}")
            
            # Test 4: QR Code
            print("\n📱 Test QR code...")
            qr_code = await manager.create_qr_code("https://example.com")
            if qr_code:
                print(f"✅ QR code: {qr_code.url}")
            
            # Test 5: TTS
            print("\n🎵 Test synthèse vocale...")
            speech = await manager.synthesize_speech(
                text="Hello, this is a test of speech synthesis"
            )
            if speech:
                print(f"✅ Audio généré: {len(speech.audio_data)} bytes")
            
            # Test 6: Polices
            print("\n🔤 Test recherche polices...")
            fonts = await manager.search_fonts("roboto", limit=3)
            if fonts:
                print(f"✅ {len(fonts)} polices trouvées")
                for font in fonts:
                    print(f"   {font.family} ({font.category})")
            
            # Test 7: Crypto
            print("\n💰 Test données crypto...")
            crypto_data = await manager.get_crypto_market_data(per_page=5)
            if crypto_data:
                print(f"✅ {len(crypto_data)} crypto récupérées")
                for coin in crypto_data[:2]:
                    print(f"   {coin.name}: ${coin.current_price}")
            
            # Test 8: Package complet
            print("\n🎁 Test package contenu complet...")
            package = await manager.create_branded_content_package(
                text="Test marketing content",
                url="https://example.com/product",
                image_prompt="Professional marketing banner"
            )
            
            success_count = sum(1 for v in package.values() if v is not None)
            print(f"✅ Package créé: {success_count}/{len(package)} éléments")
            
            # Test 9: Contenu multilingue
            print("\n🌐 Test contenu multilingue...")
            multilingual = await manager.create_multilingual_content(
                text="Welcome to our platform",
                languages=["fr", "es"],
                generate_speech=False
            )
            
            translations_count = len(multilingual["translations"])
            print(f"✅ Contenu multilingue: {translations_count} langues")
            
            # Résumé final
            print("\n📋 Résumé des APIs gratuites:")
            summary = manager.get_free_apis_summary()
            print(f"   Services totaux: {summary['total_services']}")
            print(f"   Services actifs: {summary['active_services']}")
            print(f"   Sans clé API: {summary['no_key_required']}")
            print(f"   Catégories: {len(summary['services_by_category'])}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test complet des APIs gratuites
    result = asyncio.run(test_all_free_apis())
    sys.exit(0 if result else 1)