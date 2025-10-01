#!/usr/bin/env python3
"""
🎨 FREEPIK/FLATICON API INTEGRATION
Intégration complète pour images et icônes professionnelles
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
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FreepikImage:
    """Classe pour représenter une image Freepik"""
    id: str
    title: str
    description: str
    tags: List[str]
    url: str
    thumbnail_url: str
    download_url: str
    author: str
    license: str
    dimensions: Dict[str, int]
    file_size: Optional[int] = None
    format: Optional[str] = None
    category: Optional[str] = None
    premium: bool = False
    created_at: Optional[str] = None

@dataclass
class FlaticonIcon:
    """Classe pour représenter une icône Flaticon"""
    id: str
    title: str
    description: str
    tags: List[str]
    url: str
    svg_url: str
    png_url: str
    download_url: str
    author: str
    pack_id: Optional[str] = None
    pack_name: Optional[str] = None
    license: str = "free"
    premium: bool = False
    formats: List[str] = None
    sizes: List[int] = None
    created_at: Optional[str] = None

class FreepikAPI:
    """Client API pour Freepik"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.freepik.com/v1"
        self.session = None
        self.rate_limit_remaining = 100
        self.rate_limit_reset = None
        
        # Headers par défaut
        self.headers = {
            'X-Freepik-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'IA Chéries-Platform/1.0'
        }
        
        logger.info(f"🎨 FreepikAPI initialisé avec clé: {api_key[:20]}...")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Faire une requête à l'API Freepik"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                # Mettre à jour les limites de taux
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                self.rate_limit_reset = response.headers.get('X-RateLimit-Reset')
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Requête réussie: {endpoint}")
                    return data
                elif response.status == 429:
                    logger.warning(f"⚠️ Limite de taux atteinte. Reset: {self.rate_limit_reset}")
                    raise Exception("Rate limit exceeded")
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    error_data = await response.text()
                    raise Exception(f"API Error {response.status}: {error_data}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur de requête: {e}")
            raise

    async def search_images(self, 
                          query: str, 
                          limit: int = 20,
                          category: str = None,
                          orientation: str = None,
                          min_width: int = None,
                          min_height: int = None) -> List[FreepikImage]:
        """Rechercher des images sur Freepik"""
        
        params = {
            'q': query,
            'limit': min(limit, 100),  # Max 100 par requête
        }
        
        if category:
            params['category'] = category
        if orientation:
            params['orientation'] = orientation
        if min_width:
            params['min_width'] = min_width
        if min_height:
            params['min_height'] = min_height
            
        logger.info(f"🔍 Recherche d'images: '{query}'")
        
        try:
            data = await self._make_request('resources', params)
            
            images = []
            for item in data.get('data', []):
                image = FreepikImage(
                    id=str(item.get('id')),
                    title=item.get('title', ''),
                    description=item.get('description', ''),
                    tags=item.get('tags', []),
                    url=item.get('url', ''),
                    thumbnail_url=item.get('thumbnail', {}).get('url', ''),
                    download_url=item.get('download_url', ''),
                    author=item.get('author', {}).get('name', 'Unknown'),
                    license=item.get('license', 'free'),
                    dimensions={
                        'width': item.get('width', 0),
                        'height': item.get('height', 0)
                    },
                    file_size=item.get('file_size'),
                    format=item.get('format'),
                    category=item.get('category'),
                    premium=item.get('premium', False),
                    created_at=item.get('created_at')
                )
                images.append(image)
                
            logger.info(f"✅ {len(images)} images trouvées")
            return images
            
        except Exception as e:
            logger.error(f"❌ Erreur de recherche: {e}")
            return []

    async def get_image_details(self, image_id: str) -> Optional[FreepikImage]:
        """Obtenir les détails d'une image spécifique"""
        try:
            data = await self._make_request(f'resources/{image_id}')
            
            item = data.get('data', {})
            if not item:
                return None
                
            return FreepikImage(
                id=str(item.get('id')),
                title=item.get('title', ''),
                description=item.get('description', ''),
                tags=item.get('tags', []),
                url=item.get('url', ''),
                thumbnail_url=item.get('thumbnail', {}).get('url', ''),
                download_url=item.get('download_url', ''),
                author=item.get('author', {}).get('name', 'Unknown'),
                license=item.get('license', 'free'),
                dimensions={
                    'width': item.get('width', 0),
                    'height': item.get('height', 0)
                },
                file_size=item.get('file_size'),
                format=item.get('format'),
                category=item.get('category'),
                premium=item.get('premium', False),
                created_at=item.get('created_at')
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

class FlaticonAPI:
    """Client API pour Flaticon"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.flaticon.com/v3"
        self.session = None
        self.rate_limit_remaining = 100
        self.rate_limit_reset = None
        
        # Headers par défaut
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'IA Chéries-Platform/1.0'
        }
        
        logger.info(f"🔷 FlaticonAPI initialisé avec clé: {api_key[:20]}...")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Faire une requête à l'API Flaticon"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                # Mettre à jour les limites de taux
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                self.rate_limit_reset = response.headers.get('X-RateLimit-Reset')
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Requête réussie: {endpoint}")
                    return data
                elif response.status == 429:
                    logger.warning(f"⚠️ Limite de taux atteinte. Reset: {self.rate_limit_reset}")
                    raise Exception("Rate limit exceeded")
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    error_data = await response.text()
                    raise Exception(f"API Error {response.status}: {error_data}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur de requête: {e}")
            raise

    async def search_icons(self, 
                         query: str, 
                         limit: int = 20,
                         style: str = None,
                         pack_id: str = None) -> List[FlaticonIcon]:
        """Rechercher des icônes sur Flaticon"""
        
        params = {
            'q': query,
            'limit': min(limit, 100),  # Max 100 par requête
        }
        
        if style:
            params['style'] = style
        if pack_id:
            params['pack_id'] = pack_id
            
        logger.info(f"🔍 Recherche d'icônes: '{query}'")
        
        try:
            data = await self._make_request('search/icons', params)
            
            icons = []
            for item in data.get('data', []):
                icon = FlaticonIcon(
                    id=str(item.get('id')),
                    title=item.get('title', ''),
                    description=item.get('description', ''),
                    tags=item.get('tags', []),
                    url=item.get('url', ''),
                    svg_url=item.get('images', {}).get('svg', ''),
                    png_url=item.get('images', {}).get('png', {}).get('512', ''),
                    download_url=item.get('download_url', ''),
                    author=item.get('author', {}).get('name', 'Unknown'),
                    pack_id=str(item.get('pack', {}).get('id', '')),
                    pack_name=item.get('pack', {}).get('title', ''),
                    license=item.get('license', 'free'),
                    premium=item.get('premium', False),
                    formats=item.get('formats', ['svg', 'png']),
                    sizes=[64, 128, 256, 512],
                    created_at=item.get('created_at')
                )
                icons.append(icon)
                
            logger.info(f"✅ {len(icons)} icônes trouvées")
            return icons
            
        except Exception as e:
            logger.error(f"❌ Erreur de recherche: {e}")
            return []

    async def get_icon_details(self, icon_id: str) -> Optional[FlaticonIcon]:
        """Obtenir les détails d'une icône spécifique"""
        try:
            data = await self._make_request(f'items/{icon_id}')
            
            item = data.get('data', {})
            if not item:
                return None
                
            return FlaticonIcon(
                id=str(item.get('id')),
                title=item.get('title', ''),
                description=item.get('description', ''),
                tags=item.get('tags', []),
                url=item.get('url', ''),
                svg_url=item.get('images', {}).get('svg', ''),
                png_url=item.get('images', {}).get('png', {}).get('512', ''),
                download_url=item.get('download_url', ''),
                author=item.get('author', {}).get('name', 'Unknown'),
                pack_id=str(item.get('pack', {}).get('id', '')),
                pack_name=item.get('pack', {}).get('title', ''),
                license=item.get('license', 'free'),
                premium=item.get('premium', False),
                formats=item.get('formats', ['svg', 'png']),
                sizes=[64, 128, 256, 512],
                created_at=item.get('created_at')
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def get_icon_packs(self, limit: int = 20) -> List[Dict]:
        """Obtenir les packs d'icônes populaires"""
        params = {'limit': min(limit, 100)}
        
        try:
            data = await self._make_request('packs', params)
            return data.get('data', [])
        except Exception as e:
            logger.error(f"❌ Erreur de récupération des packs: {e}")
            return []

class FreepikFlaticonIntegration:
    """Intégration unifiée Freepik/Flaticon"""
    
    def __init__(self, freepik_key: str, flaticon_key: str):
        self.freepik_api = FreepikAPI(freepik_key)
        self.flaticon_api = FlaticonAPI(flaticon_key)
        
        logger.info("🎨 Intégration Freepik/Flaticon initialisée")

    async def __aenter__(self):
        """Initialiser les sessions async"""
        await self.freepik_api.__aenter__()
        await self.flaticon_api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer les sessions async"""
        await self.freepik_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.flaticon_api.__aexit__(exc_type, exc_val, exc_tb)

    async def search_all_assets(self, query: str, limit: int = 10) -> Dict:
        """Rechercher à la fois des images et des icônes"""
        try:
            # Recherche en parallèle
            images_task = self.freepik_api.search_images(query, limit)
            icons_task = self.flaticon_api.search_icons(query, limit)
            
            images, icons = await asyncio.gather(images_task, icons_task)
            
            return {
                'images': images,
                'icons': icons,
                'total_results': len(images) + len(icons),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur de recherche combinée: {e}")
            return {'images': [], 'icons': [], 'total_results': 0, 'error': str(e)}

    async def get_content_suggestions(self, content_type: str, topic: str) -> Dict:
        """Obtenir des suggestions de contenu visuel"""
        suggestions = {}
        
        # Mots-clés basés sur le type de contenu
        if content_type == 'social_media':
            keywords = [f"{topic} social", f"{topic} post", f"{topic} story"]
        elif content_type == 'blog':
            keywords = [f"{topic} article", f"{topic} blog", f"{topic} content"]
        elif content_type == 'marketing':
            keywords = [f"{topic} marketing", f"{topic} promotion", f"{topic} campaign"]
        else:
            keywords = [topic]
            
        for keyword in keywords:
            result = await self.search_all_assets(keyword, 5)
            if result['total_results'] > 0:
                suggestions[keyword] = result
                
        return suggestions

    def get_rate_limit_status(self) -> Dict:
        """Obtenir le statut des limites de taux"""
        return {
            'freepik': {
                'remaining': self.freepik_api.rate_limit_remaining,
                'reset': self.freepik_api.rate_limit_reset
            },
            'flaticon': {
                'remaining': self.flaticon_api.rate_limit_remaining,
                'reset': self.flaticon_api.rate_limit_reset
            }
        }

# Fonctions utilitaires pour l'authentification
def load_credentials() -> tuple:
    """Charger les credentials depuis les variables d'environnement"""
    freepik_key = os.getenv('FREEPIK_API_KEY')
    flaticon_key = os.getenv('FLATICON_API_KEY')
    
    if not freepik_key or not flaticon_key:
        raise ValueError("Les clés API Freepik/Flaticon ne sont pas configurées")
        
    return freepik_key, flaticon_key

async def test_integration():
    """Tester l'intégration Freepik/Flaticon"""
    try:
        freepik_key, flaticon_key = load_credentials()
        
        async with FreepikFlaticonIntegration(freepik_key, flaticon_key) as integration:
            # Test de recherche
            results = await integration.search_all_assets("business", 3)
            
            print(f"✅ Test réussi: {results['total_results']} résultats trouvés")
            print(f"📸 Images: {len(results['images'])}")
            print(f"🔷 Icônes: {len(results['icons'])}")
            
            # Afficher quelques exemples
            if results['images']:
                print("\n📸 Exemples d'images:")
                for img in results['images'][:2]:
                    print(f"  - {img.title} par {img.author}")
                    
            if results['icons']:
                print("\n🔷 Exemples d'icônes:")
                for icon in results['icons'][:2]:
                    print(f"  - {icon.title} du pack {icon.pack_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)