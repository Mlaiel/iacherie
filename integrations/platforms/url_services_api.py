#!/usr/bin/env python3
"""
🔗 QR CODE & URL SERVICES API INTEGRATION
Services gratuits pour QR codes et raccourcissement d'URLs
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
import urllib.parse
import base64
from io import BytesIO

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QRCode:
    """Données d'un QR code généré"""
    data: str
    url: str
    size: str
    format: str
    error_correction: str
    encoding: str = "UTF-8"
    border: int = 0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ShortURL:
    """URL raccourcie"""
    original_url: str
    short_url: str
    service: str
    custom_alias: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class QRServerAPI:
    """Client pour QR Server API - Service gratuit de génération QR codes"""
    
    def __init__(self):
        self.base_url = "https://api.qrserver.com/v1/create-qr-code"
        self.session = None
        
        # Tailles disponibles
        self.available_sizes = [
            "100x100", "150x150", "200x200", "250x250", "300x300",
            "400x400", "500x500", "600x600", "800x800", "1000x1000"
        ]
        
        # Niveaux de correction d'erreur
        self.error_levels = {
            "L": "Low (~7%)",
            "M": "Medium (~15%)",
            "Q": "Quartile (~25%)",
            "H": "High (~30%)"
        }
        
        logger.info("🔗 QRServerAPI initialisé - Service 100% gratuit")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def generate_qr_code(self, 
                             data: str,
                             size: str = "300x300",
                             format: str = "png",
                             error_correction: str = "M",
                             border: int = 0,
                             color: str = "000000",
                             bgcolor: str = "ffffff") -> Optional[QRCode]:
        """Générer un QR code"""
        
        if not data.strip():
            logger.warning("⚠️ Données vides pour QR code")
            return None
            
        # Vérifier la taille
        if size not in self.available_sizes:
            logger.warning(f"⚠️ Taille {size} non disponible, utilisation de 300x300")
            size = "300x300"
            
        # Vérifier le niveau de correction
        if error_correction not in self.error_levels:
            logger.warning(f"⚠️ Niveau de correction {error_correction} invalide, utilisation de M")
            error_correction = "M"
            
        logger.info(f"🔗 Génération QR code: {len(data)} caractères, taille {size}")
        
        try:
            # Construire les paramètres
            params = {
                "data": data,
                "size": size,
                "format": format,
                "ecc": error_correction,
                "border": border,
                "color": color,
                "bgcolor": bgcolor
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    # L'URL complète avec paramètres
                    full_url = str(response.url)
                    
                    qr_code = QRCode(
                        data=data,
                        url=full_url,
                        size=size,
                        format=format,
                        error_correction=error_correction,
                        border=border
                    )
                    
                    logger.info(f"✅ QR code généré: {full_url}")
                    return qr_code
                else:
                    logger.error(f"❌ Erreur de génération QR: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de génération QR: {e}")
            return None

    async def download_qr_code(self, qr_code: QRCode, filepath: str) -> bool:
        """Télécharger un QR code vers un fichier"""
        try:
            async with self.session.get(qr_code.url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Créer le dossier si nécessaire
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Écrire le fichier
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"💾 QR code sauvegardé: {filepath}")
                    return True
                else:
                    logger.error(f"❌ Erreur de téléchargement: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur de sauvegarde: {e}")
            return False

    async def generate_multiple_qr_codes(self, 
                                       data_list: List[str],
                                       size: str = "300x300",
                                       format: str = "png") -> List[Optional[QRCode]]:
        """Générer plusieurs QR codes en parallèle"""
        
        tasks = []
        for data in data_list:
            task = self.generate_qr_code(data, size, format)
            tasks.append(task)
        
        logger.info(f"🔗 Génération de {len(data_list)} QR codes en parallèle...")
        
        results = await asyncio.gather(*tasks)
        successful = sum(1 for r in results if r is not None)
        
        logger.info(f"✅ {successful}/{len(data_list)} QR codes générés")
        return results

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur le service QR"""
        return {
            'service': 'QR Server',
            'base_url': self.base_url,
            'features': [
                'Free QR code generation',
                'Multiple sizes available',
                'PNG and other formats',
                'Custom colors',
                'Error correction levels',
                'No API key required'
            ],
            'available_sizes': self.available_sizes,
            'error_levels': self.error_levels,
            'rate_limit': 'None (unlimited free)'
        }

class TinyURLAPI:
    """Client pour TinyURL - Service avec API key pour fonctionnalités avancées"""
    
    def __init__(self, api_key: Optional[str] = None):
        # TinyURL avec clé API pour alias personnalisés et analytics
        self.api_key = api_key or "V6nENR9gI5ESnWfKRORk715xHV2kywjjvAPkry5OhlDamik7hM5X1FMfjB7u"
        
        if self.api_key:
            self.base_url = "https://api.tinyurl.com/create"
            self.alias_url = "https://api.tinyurl.com/alias"
            logger.info("🔗 TinyURLAPI initialisé - Mode API Pro avec clé")
        else:
            self.base_url = "https://tinyurl.com/api-create.php"
            logger.info("🔗 TinyURLAPI initialisé - Mode gratuit")
            
        self.session = None

    async def __aenter__(self):
        """Initialiser la session async"""
        headers = {'Content-Type': 'application/json'}
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def shorten_url(self, url: str, custom_alias: Optional[str] = None) -> Optional[ShortURL]:
        """Raccourcir une URL"""
        
        if not url.strip():
            logger.warning("⚠️ URL vide fournie")
            return None
            
        # Vérifier que l'URL est valide
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.warning("⚠️ URL doit commencer par http:// ou https://")
            return None
            
        logger.info(f"🔗 Raccourcissement URL: {url}")
        
        try:
            if self.api_key:
                # Mode API avec clé - plus de fonctionnalités
                payload = {
                    "url": url,
                    "domain": "tinyurl.com"
                }
                
                if custom_alias:
                    payload["alias"] = custom_alias
                
                async with self.session.post(self.base_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        short_url = data.get("data", {}).get("tiny_url")
                        
                        if short_url:
                            result = ShortURL(
                                original_url=url,
                                short_url=short_url,
                                service="TinyURL Pro",
                                custom_alias=custom_alias
                            )
                            
                            logger.info(f"✅ URL raccourcie (API): {short_url}")
                            return result
                        else:
                            logger.error(f"❌ Réponse API invalide: {data}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur API raccourcissement: {response.status} - {error_text}")
                        return None
                        
            else:
                # Mode gratuit sans clé
                params = {"url": url}
                if custom_alias:
                    params["alias"] = custom_alias
                    
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        short_url = await response.text()
                        short_url = short_url.strip()
                        
                        # Vérifier si c'est une URL valide
                        if short_url.startswith('https://tinyurl.com/'):
                            result = ShortURL(
                                original_url=url,
                                short_url=short_url,
                                service="TinyURL",
                                custom_alias=custom_alias
                            )
                            
                            logger.info(f"✅ URL raccourcie: {short_url}")
                            return result
                        else:
                            logger.error(f"❌ Réponse invalide: {short_url}")
                            return None
                    else:
                        logger.error(f"❌ Erreur de raccourcissement: {response.status}")
                        return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de raccourcissement: {e}")
            return None

    async def shorten_multiple_urls(self, urls: List[str]) -> List[Optional[ShortURL]]:
        """Raccourcir plusieurs URLs en parallèle"""
        
        tasks = []
        for url in urls:
            task = self.shorten_url(url)
            tasks.append(task)
        
        logger.info(f"🔗 Raccourcissement de {len(urls)} URLs en parallèle...")
        
        results = await asyncio.gather(*tasks)
        successful = sum(1 for r in results if r is not None)
        
        logger.info(f"✅ {successful}/{len(urls)} URLs raccourcies")
        return results

class URLServicesIntegration:
    """Intégration combinée QR codes + URL raccourcies"""
    
    def __init__(self):
        self.qr_api = QRServerAPI()
        self.tiny_api = TinyURLAPI()
        
        logger.info("🔗 URL Services Integration initialisée")

    async def __aenter__(self):
        """Initialiser les sessions"""
        await self.qr_api.__aenter__()
        await self.tiny_api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer les sessions"""
        await self.qr_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.tiny_api.__aexit__(exc_type, exc_val, exc_tb)

    async def create_short_url_with_qr(self, 
                                     url: str,
                                     custom_alias: Optional[str] = None,
                                     qr_size: str = "300x300") -> Dict[str, Any]:
        """Créer une URL raccourcie + son QR code"""
        
        # Raccourcir l'URL
        short_url_result = await self.tiny_api.shorten_url(url, custom_alias)
        
        if not short_url_result:
            return {"success": False, "error": "Failed to shorten URL"}
        
        # Générer le QR code de l'URL raccourcie
        qr_result = await self.qr_api.generate_qr_code(
            data=short_url_result.short_url,
            size=qr_size
        )
        
        if not qr_result:
            return {
                "success": True,
                "short_url": short_url_result,
                "qr_code": None,
                "warning": "QR code generation failed"
            }
        
        return {
            "success": True,
            "short_url": short_url_result,
            "qr_code": qr_result,
            "combined_url": short_url_result.short_url,
            "qr_image_url": qr_result.url
        }

    async def batch_process_urls(self, 
                               urls: List[str],
                               generate_qr: bool = True,
                               qr_size: str = "200x200") -> List[Dict[str, Any]]:
        """Traiter plusieurs URLs en lot"""
        
        results = []
        
        for url in urls:
            result = await self.create_short_url_with_qr(
                url=url,
                qr_size=qr_size if generate_qr else None
            )
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success", False))
        logger.info(f"✅ {successful}/{len(urls)} URLs traitées avec succès")
        
        return results

# Fonctions utilitaires
async def test_integration():
    """Tester l'intégration des services URL"""
    try:
        async with URLServicesIntegration() as services:
            # Test 1: QR code simple
            print("🔗 Test génération QR code...")
            qr_result = await services.qr_api.generate_qr_code(
                data="https://github.com/your-repo",
                size="300x300"
            )
            
            if qr_result:
                print(f"✅ QR code généré: {qr_result.url}")
                print(f"📄 Données: {qr_result.data}")
                print(f"📏 Taille: {qr_result.size}")
            
            # Test 2: URL raccourcie
            print("\n🔗 Test raccourcissement URL...")
            short_result = await services.tiny_api.shorten_url(
                "https://www.example.com/very/long/url/that/needs/shortening"
            )
            
            if short_result:
                print(f"✅ URL raccourcie: {short_result.short_url}")
                print(f"📄 Original: {short_result.original_url}")
            
            # Test 3: Combiné (URL courte + QR code)
            print("\n🔗 Test combiné (URL + QR)...")
            combined_result = await services.create_short_url_with_qr(
                url="https://www.google.com/search?q=example+search+query",
                qr_size="250x250"
            )
            
            if combined_result.get("success"):
                print("✅ Traitement combiné réussi:")
                print(f"   🔗 URL courte: {combined_result['short_url'].short_url}")
                print(f"   📱 QR code: {combined_result['qr_code'].url}")
            
            # Test 4: Informations services
            print("\n📊 Informations services...")
            qr_info = services.qr_api.get_service_info()
            print(f"✅ QR Service: {qr_info['service']}")
            print(f"📏 Tailles: {len(qr_info['available_sizes'])} options")
            
            # Test 5: Traitement en lot
            print("\n🔗 Test traitement en lot...")
            test_urls = [
                "https://www.example1.com",
                "https://www.example2.com/path",
                "https://www.example3.com/longer/path/here"
            ]
            
            batch_results = await services.batch_process_urls(test_urls, generate_qr=True)
            successful_batch = sum(1 for r in batch_results if r.get("success"))
            print(f"✅ Lot traité: {successful_batch}/{len(test_urls)} succès")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)